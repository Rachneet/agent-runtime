import os
import shutil
from datetime import datetime, timedelta
from typing import List, Optional

import bcrypt
import docker
import jwt
import uvicorn
from docker.errors import APIError, ImageNotFound
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, Field

load_dotenv()

from src.backend.container_config import ContainerConfig
from src.logging_config import setup_logging

logger = setup_logging(log_file="app.log", log_level="INFO", service_name="fastapi_app")

# ========= OAUTH for the API ==========

# Security Config
SECRET_KEY = os.getenv("SECRET_KEY", "codewithrach")
ALGORITHM = "HS256"
TOKEN_EXPIRES = 30

# Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # generate token

# Security functions
def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Truncates password to 72 bytes if necessary (bcrypt limitation).
    """
    # Ensure password is not too long (bcrypt limit is 72 bytes)
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        logger.warning(f"Password is longer than 72 bytes, truncating to 72 bytes")
        password_bytes = password_bytes[:72]
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    """
    try:
        # Ensure password is not too long
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


# Fake user database (replace with real database in production)
fake_users_db = {
    "agent_user": {
        "username": os.getenv("OAUTH_USERNAME"),
        "full_name": "AI Agent User",
        "email": "agent@example.com",
        "hashed_password": hash_password(os.getenv("OAUTH_PASSWORD")),
        "disabled": False,
    }
}

# ========= Pydantic Models =========


class Token(BaseModel):
    """OAuth2 token response."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token payload data."""
    username: Optional[str] = None


class User(BaseModel):
    """User model."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(User):
    """User model with hashed password."""
    hashed_password: str


def get_user(username: str) -> Optional[UserInDB]:
    """Get user from database."""
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    """Authenticate a user."""
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Validate token and return current user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Check if user is active."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# ========= Pydantic Models for the API =========


class FilePayload(BaseModel):
    """A file to be written to the runtime environment."""

    filename: str
    content: str


class JobPayload(BaseModel):
    """The job request, containing files and a command."""

    files: List[FilePayload]
    command: str = Field(..., example="pytest test_payment_validator.py -v")


class JobResult(BaseModel):
    """The result of the job execution."""

    success: bool
    exit_code: int
    stdout: str
    stderr: str


# ======== FastAPI App =========
app = FastAPI(
    title="Secure Agent Runtime Service",
    description="Executes arbitrary code in an isolated Docker container.",
)


@app.get("/", summary="Health check endpoint.")
def read_root():
    return {"status": "Secure Agent Runtime is online."}


@app.post("/token", response_model=Token, summary="OAuth2 token endpoint")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login endpoint.
    Use this endpoint to get an access token.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=TOKEN_EXPIRES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/run", summary="Run a new execution job.", response_model=JobResult)
def run_job(job: JobPayload, current_user: User = Depends(get_current_active_user)):
    """
    Runs a command in a new, isolated Docker container.
    """
    # Initialize Docker client
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        raise HTTPException(
            status_code=500, detail="Docker is not running or not configured correctly."
        )

    # Create a temporary directory where the execution should take place
    temp_dir = os.path.abspath(f"./runtime_sandbox_{os.urandom(4).hex()}")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    container = None
    config = ContainerConfig()

    try:
        # Write files and CALCULATE PYTHONPATH
        # We want to find every directory where we put a file
        unique_dirs = set()
        unique_dirs.add("/app")  # Always add root

        for file in job.files:
            # Extract directory from filename (e.g., "demo_project" from "demo_project/file.py")
            directory = os.path.dirname(file.filename)
            if directory:
                unique_dirs.add(f"/app/{directory}")

            # Write file
            file_path = os.path.join(temp_dir, file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file.content)

        # Join them into a PYTHONPATH string (e.g., "/app:/app/demo_project")
        python_path = ":".join(unique_dirs)
        logger.info(f"Generated PYTHONPATH: {python_path}")  # For debug visibility

        # Define command to execute
        full_command = f"/bin/sh -c 'pip install pytest flake8 && {job.command}'"

        # Run the container
        try:
            container = client.containers.run(
                image="python:3.10-slim",
                command=full_command,
                volumes={temp_dir: {"bind": "/app", "mode": "rw"}},
                working_dir="/app",
                environment={"PYTHONPATH": python_path},
                # ----------resource limits------------
                cpu_quota=config.cpu_quota,
                cpu_period=config.cpu_period,
                cpu_shares=config.cpu_shares,

                mem_limit=config.memory_limit,
                memswap_limit=config.memory_swap,
                mem_reservation=config.memory_reservation,

                pids_limit=config.pids_limit,

                # network_disabled=config.enable_network,

                # read_only=config.read_only_root,
                # tmpfs={"/tmp": f"size={config.tmpfs_size}"} if config.read_only_root else None,

                # cap_drop=["ALL"] if config.drop_all_capabilities else None,
                # security_opt=["no-new-privileges"] if config.no_new_privileges else None,
                
                # ----------------------------------------------
                remove=False,
                detach=True,
                stdout=True,
                stderr=True,
            )

            result = container.wait()
            exit_code = result.get("StatusCode", 0)

            logs = container.logs(stdout=True, stderr=True)
            decoded_logs = logs.decode("utf-8", errors="replace")

            stdout = decoded_logs
            stderr = ""
            success = exit_code == 0

        except ImageNotFound:
            raise HTTPException(
                status_code=500, detail="Python 3.10 Docker image not found."
            )
        except APIError as e:
            raise HTTPException(status_code=500, detail=f"Docker API Error: {e}")

        return JobResult(
            success=success, exit_code=exit_code, stdout=stdout, stderr=stderr
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # remove ephemeral container
        if container:
            try:
                container.remove(force=True)
            except Exception:
                pass
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    print("Starting Secure Agent Runtime Service on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
