import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import docker
from docker.errors import ContainerError, ImageNotFound, APIError
import tempfile
import os
import shutil
from typing import List, Dict

# --- Pydantic Models for the API ---

class FilePayload(BaseModel):
    """A file to be written to the runtime environment."""
    filename: str
    content: str

class JobPayload(BaseModel):
    """The job request, containing files and a command."""
    files: List[FilePayload]
    command: str = Field(
        ..., 
        example="pytest test_payment_validator.py -v"
    )

class JobResult(BaseModel):
    """The result of the job execution."""
    success: bool
    exit_code: int
    stdout: str
    stderr: str

# --- FastAPI App ---
app = FastAPI(
    title="Secure Agent Runtime Service",
    description="Executes arbitrary code in an isolated Docker container."
)

@app.get("/", summary="Health check endpoint.")
def read_root():
    return {"status": "Secure Agent Runtime is online."}

@app.post("/run", summary="Run a new execution job.", response_model=JobResult)
def run_job(job: JobPayload):
    """
    Runs a command in a new, isolated Docker container.
    Automatically sets PYTHONPATH based on file locations.
    """
    # 1. Initialize Docker client
    try:
        client = docker.from_env()
    except docker.errors.DockerException:
        raise HTTPException(
            status_code=500, 
            detail="Docker is not running or not configured correctly."
        )

    # 2. Create a temporary directory
    temp_dir = os.path.abspath(f"./runtime_sandbox_{os.urandom(4).hex()}")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    container = None 

    try:
        # 3. Write files and CALCULATE PYTHONPATH
        # We want to find every directory where we put a file
        unique_dirs = set()
        unique_dirs.add("/app") # Always add root
        
        for file in job.files:
            # Extract directory from filename (e.g., "demo_project" from "demo_project/file.py")
            directory = os.path.dirname(file.filename)
            if directory:
                unique_dirs.add(f"/app/{directory}")
            
            # Write file
            file_path = os.path.join(temp_dir, file.filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file.content)
        
        # Join them into a PYTHONPATH string (e.g., "/app:/app/demo_project")
        python_path = ":".join(unique_dirs)
        print(f"Generated PYTHONPATH: {python_path}") # For debug visibility

        # 4. Define command
        full_command = f"/bin/sh -c 'pip install pytest && {job.command}'"
       
        # 5. Run the container
        try:
            container = client.containers.run(
                image="python:3.10-slim",
                command=full_command,
                volumes={
                    temp_dir: {'bind': '/app', 'mode': 'rw'}
                },
                working_dir="/app",
                # --- CRITICAL CHANGE: Inject the PYTHONPATH ---
                environment={
                    "PYTHONPATH": python_path
                },
                # ----------------------------------------------
                remove=False, 
                detach=True, 
                stdout=True,
                stderr=True
            )
            
            result = container.wait()
            exit_code = result.get('StatusCode', 0)
            
            logs = container.logs(stdout=True, stderr=True)
            decoded_logs = logs.decode('utf-8', errors='replace')
            
            stdout = decoded_logs
            stderr = ""
            success = (exit_code == 0)

        except ImageNotFound:
            raise HTTPException(status_code=500, detail="Python 3.10 Docker image not found.")
        except APIError as e:
            raise HTTPException(status_code=500, detail=f"Docker API Error: {e}")

        return JobResult(
            success=success,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
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