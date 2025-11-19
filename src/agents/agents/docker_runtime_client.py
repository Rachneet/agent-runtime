import httpx
from typing import List, Dict, Any
from src.logging_config import setup_logging
from src.agents.orchestration.states import AgentState

logger = setup_logging(
    service_name="docker_runtime_client", 
    log_file="app.log", 
    log_level="INFO"
)

class DockerRuntimeClient:
    """
    Client to submit jobs to the Secure Docker Runtime Service.
    This replaces the old RuntimeExecutionTool.
    """
    
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
        self.client = httpx.Client()

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
                    "error": "No command provided by Task Agent."
                }
            }

        logger.info(f"Preparing to send {len(files)} files to runtime:")
        for f in files:
            content_len = len(f.get('content', ''))
            filename = f.get('filename')
            logger.info(f"  - File: {filename} | Content Length: {content_len} chars")
            
            # SAFETY CHECK: Warn if content is empty
            if content_len == 0:
                logger.warning(f"WARNING: Content for {filename} is EMPTY!")

        job_payload = {
            "files": files,
            "command": command
        }
        
        logger.info(f"Submitting job to Docker Runtime: {command}")
        
        try:
            response = self.client.post(f"{self.base_url}/run", json=job_payload, timeout=300.0)
            response.raise_for_status()  # Raise exception for 4xx/5xx
            
            result = response.json()
            logger.info(f"Job completed with exit code: {result.get('exit_code')}")

            if result.get('exit_code') == 1:
                result['success'] = True
                logger.info("Job finished with Exit Code 1 (Some Tests Failed). Marking as Runtime Success.")

            logger.info(f"Job completed with exit code: {result.get('exit_code')}")
            state["execution_results"] = result
            return state
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Error from runtime: {e.response.status_code} - {e.response.text}")
            state["execution_results"] = {
                "success": False, 
                "stdout": "", 
                "stderr": e.response.text, 
                "exit_code": -1
                }
            return state
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to Docker Runtime Service at {self.base_url}: {e}")
            state["execution_results"] = {
                "success": False, 
                "stdout": "", 
                "stderr": f"Failed to connect to runtime service: {e}", 
                "exit_code": -1
            }
            return state