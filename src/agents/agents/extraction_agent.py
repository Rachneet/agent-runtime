import os
from pathlib import Path
from typing import Dict, List, Optional

from src.agents.orchestration.states import AgentState
from src.logging_config import setup_logging

logger = setup_logging(
    service_name="extraction_agent", log_file="app.log", log_level="INFO"
)


class CodeExtractionAgent:
    """Agent to extract code content from files based on paths."""

    def __init__(self, base_path: str = "."):
        """
        Initialize the extraction agent.

        Args:
            base_path: Base directory path for resolving relative paths
        """
        self.base_path = Path(base_path).resolve()

    def extraction_node(self, state: AgentState) -> Dict:
        """
        Extract code content from files specified in agent result.

        Args:
            state: Agent state

        Returns:
            Dict with file contents and command
        """
        files = state["search_results"].get("files", [])
        command = state["search_results"].get("command", "")

        result = {"command": command, "files": []}

        for file_path in files:
            content = self._read_file(file_path)
            logger.info(len(content))
            result["files"].append({"filename": file_path, "content": content})

        # update state
        state["extraction_results"] = result
        logger.info("Extraction finished ...")
        # logger.info(f"Results: {state['extraction_results']}")

        return state

    def _read_file(self, file_path: str) -> Optional[str]:
        """
        Read content from a single file.

        Args:
            file_path: Path to the file (relative or absolute)

        Returns:
            File content as string, or error message if file cannot be read
        """
        try:
            # Handle both relative and absolute paths
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path

            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return f"ERROR: File not found - {file_path}"
        except PermissionError:
            return f"ERROR: Permission denied - {file_path}"
        except Exception as e:
            return f"ERROR: {str(e)} - {file_path}"


# Example usage:
if __name__ == "__main__":
    # Your agent result
    agent_result = {
        "files": [
            "src/demo_project/payment_validator.py",
            "src/demo_project/test_payment_validator.py",
        ],
        "command": "flake8 src/demo_project/payment_validator.py src/demo_project/test_payment_validator.py",
    }

    # Create extraction agent
    extractor = CodeExtractionAgent(base_path=".")

    # Extract code (simple version)
    result = extractor.extraction_node(agent_result)

    print("Command:", result["extraction_results"]["command"])
    print("\nFiles extracted:")
    print(result["extraction_results"]["files"])
