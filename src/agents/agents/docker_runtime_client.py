from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx

from src.agents.orchestration.states import AgentState
from src.logging_config import setup_logging

logger = setup_logging(
    service_name="docker_runtime_client", log_file="app.log", log_level="INFO"
)


class DockerRuntimeClient:
    """
    Client to submit jobs to the Secure Docker Runtime Service.
    This replaces the old RuntimeExecutionTool.
    """

    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.client = httpx.Client()

        import os
        self.username = os.getenv("OAUTH_USERNAME", "agent_user")
        self.password = os.getenv("OAUTH_PASSWORD", "secret_agent_password")
        
        # Token management
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        
        # Authenticate on initialization
        self._authenticate()

    def _authenticate(self) -> None:
        """
        Authenticate with the runtime service and obtain an access token.
        """
        logger.info("Authenticating with Docker Runtime Service...")
        
        try:
            response = self.client.post(
                f"{self.base_url}/token",
                data={
                    "username": self.username,
                    "password": self.password
                },
                timeout=10.0
            )
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            
            # Assume token expires in 30 minutes (adjust based on your server config)
            # Subtract 5 minutes as buffer to refresh before actual expiry
            self.token_expiry = datetime.now() + timedelta(minutes=25)
            
            logger.info("✓ Successfully authenticated with Docker Runtime Service")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Authentication failed: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to authenticate with runtime service: {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to runtime service for authentication: {e}")
            raise Exception(f"Failed to connect to runtime service: {e}")
        
    def _is_token_expired(self) -> bool:
        """Check if the current token is expired or about to expire."""
        if not self.access_token or not self.token_expiry:
            return True
        return datetime.now() >= self.token_expiry

    def _ensure_authenticated(self) -> None:
        """Ensure we have a valid token, re-authenticate if needed."""
        if self._is_token_expired():
            logger.info("Token expired or missing, re-authenticating...")
            self._authenticate()

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get the authorization headers with a valid token."""
        self._ensure_authenticated()
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def runtime_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Submits a job to the runtime service.

        Args:
            command: The command to execute (e.g., "pytest test_foo.py")
            files: A list of {"filename": "...", "content": "..."} dicts

        Returns:
            A dictionary with the execution results.
        """
        files = state["extraction_results"].get("files", [])
        command = state["extraction_results"].get("command", "")

        logger.info(f"RUNTIME: Receiving job. Command: '{command}' Files: {len(files)}")

        # Safety check
        if not command:
            return {
                "execution_results": {
                    "success": False,
                    "error": "No command provided by Task Agent.",
                }
            }

        logger.info(f"Preparing to send {len(files)} files to runtime:")
        for f in files:
            content_len = len(f.get("content", ""))
            filename = f.get("filename")
            logger.info(f"  - File: {filename} | Content Length: {content_len} chars")

            # SAFETY CHECK: Warn if content is empty
            if content_len == 0:
                logger.warning(f"WARNING: Content for {filename} is EMPTY!")

        job_payload = {"files": files, "command": command}

        logger.info(f"Submitting job to Docker Runtime: {command}")

        try:
            # get auth headers
            headers = self._get_auth_headers()

            response = self.client.post(
                f"{self.base_url}/run", 
                json=job_payload, 
                headers=headers,
                timeout=300.0
            )
            response.raise_for_status()  # Raise exception for 4xx/5xx

            result = response.json()
            logger.info(f"Job completed with exit code: {result.get('exit_code')}")

            if result.get("exit_code") == 1:
                result["success"] = True
                logger.info(
                    "Job finished with Exit Code 1 (Some Tests Failed). Marking as Runtime Success."
                )

            logger.info(f"Job completed with exit code: {result.get('exit_code')}")
            state["execution_results"] = result
            return state

        except httpx.HTTPStatusError as e:
            # Handle 401 specifically - might need re-authentication
            if e.response.status_code == 401:
                logger.warning("Received 401 Unauthorized, attempting to re-authenticate...")
                try:
                    self._authenticate()
                    # Retry the request once with new token
                    headers = self._get_auth_headers()
                    response = self.client.post(
                        f"{self.base_url}/run", 
                        json=job_payload, 
                        headers=headers,
                        timeout=300.0
                    )
                    response.raise_for_status()
                    result = response.json()
                    state["execution_results"] = result
                    return state
                except Exception as retry_error:
                    logger.error(f"Retry after re-authentication failed: {retry_error}")
            
            logger.error(
                f"HTTP Error from runtime: {e.response.status_code} - {e.response.text}"
            )
            state["execution_results"] = {
                "success": False,
                "stdout": "",
                "stderr": e.response.text,
                "exit_code": -1,
            }
            return state
            
        except httpx.RequestError as e:
            logger.error(
                f"Failed to connect to Docker Runtime Service at {self.base_url}: {e}"
            )
            state["execution_results"] = {
                "success": False,
                "stdout": "",
                "stderr": f"Failed to connect to runtime service: {e}",
                "exit_code": -1,
            }
            return state

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
