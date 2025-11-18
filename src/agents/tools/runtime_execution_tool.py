"""
Runtime Execution Tool - Correct Version for Executor Agent

Works with the actual output from your Researcher Agent.
Handles files parameter that Executor passes.
"""

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional, Dict
import subprocess
import tempfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class RuntimeExecutionInput(BaseModel):
    """Input for runtime execution"""
    command: str = Field(
        description="Command to execute (e.g., 'pytest test_file.py -v')"
    )
    files: Optional[Dict[str, str]] = Field(
        default=None,
        description="Files to create before execution: {filename: content}"
    )
    working_directory: str = Field(
        default="/workspace",
        description="Working directory for command execution"
    )


class RuntimeExecutionTool(BaseTool):
    """
    Execute commands in isolated runtime environment.
    
    This tool:
    - Creates files from Knowledge Graph data
    - Executes commands (pytest, python, etc.)
    - Returns formatted results
    - Runs in isolated temp directories (simulates Docker)
    
    For production: Replace subprocess with actual Docker API calls.
    For demo: Uses temp directories with subprocess (works perfectly!)
    """
    
    name: str = "execute_in_runtime"
    description: str = """
Execute commands in a secure isolated runtime environment.

Use this tool to run tests, execute code, or run any commands.

The tool will:
1. Create any provided files in a clean environment
2. Execute the command
3. Return the results (stdout, stderr, exit code)

IMPORTANT: Always provide both command AND files dict!

Example:
execute_in_runtime(
    command="pytest test_file.py -v",
    files={"test_file.py": "<test code>", "source.py": "<source code>"}
)
"""
    args_schema: type[BaseModel] = RuntimeExecutionInput
    
    def _run(
        self,
        command: str,
        files: Optional[Dict[str, str]] = None,
        working_directory: str = "/workspace"
    ) -> str:
        """
        Execute command in isolated environment.
        
        Args:
            command: Shell command to execute
            files: Dict of {filename: content} to create
            working_directory: Ignored (uses temp dir)
            
        Returns:
            Formatted execution results
        """
        
        logger.info(f"🐳 Runtime: Executing '{command}'")
        
        # Create isolated environment (temp directory simulates container)
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            try:
                # Step 1: Create files
                if files:
                    logger.info(f"📝 Runtime: Creating {len(files)} file(s)")
                    for filename, content in files.items():
                        file_path = tmpdir_path / filename
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(content)
                        logger.info(f"   ✓ Created: {filename} ({len(content)} chars)")
                
                # Step 2: Execute command
                logger.info(f"⚙️  Runtime: Running command...")
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                # Step 3: Format results for agent
                output = self._format_results(
                    command=command,
                    files=files,
                    returncode=result.returncode,
                    stdout=result.stdout,
                    stderr=result.stderr
                )
                
                if result.returncode == 0:
                    logger.info(f"✅ Runtime: Execution succeeded")
                else:
                    logger.info(f"❌ Runtime: Execution failed (exit code: {result.returncode})")
                
                return output
                
            except subprocess.TimeoutExpired:
                error_msg = "❌ Runtime: Execution timed out (60s limit)"
                logger.error(error_msg)
                return self._format_error(command, "Timeout after 60 seconds")
                
            except Exception as e:
                error_msg = f"❌ Runtime: Execution error: {str(e)}"
                logger.error(error_msg)
                return self._format_error(command, str(e))
    
    def _format_results(
        self,
        command: str,
        files: Optional[Dict[str, str]],
        returncode: int,
        stdout: str,
        stderr: str
    ) -> str:
        """Format execution results for agent consumption"""
        
        lines = []
        lines.append("=" * 70)
        lines.append("RUNTIME EXECUTION RESULTS")
        lines.append("=" * 70)
        lines.append(f"\nCommand: {command}")
        lines.append(f"Exit Code: {returncode}")
        
        if files:
            lines.append(f"\nFiles Executed:")
            for filename in files.keys():
                lines.append(f"  - {filename}")
        
        if stdout:
            lines.append(f"\n--- Output ---")
            lines.append(stdout.strip())
        
        if stderr:
            lines.append(f"\n--- Errors ---")
            lines.append(stderr.strip())
        
        lines.append("\n" + "=" * 70)
        
        if returncode == 0:
            lines.append("✅ EXECUTION SUCCESSFUL")
        else:
            lines.append("❌ EXECUTION FAILED")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _format_error(self, command: str, error: str) -> str:
        """Format error message"""
        lines = []
        lines.append("=" * 70)
        lines.append("RUNTIME EXECUTION RESULTS")
        lines.append("=" * 70)
        lines.append(f"\nCommand: {command}")
        lines.append(f"Exit Code: 1")
        lines.append(f"\n--- Error ---")
        lines.append(error)
        lines.append("\n" + "=" * 70)
        lines.append("❌ EXECUTION FAILED")
        lines.append("=" * 70)
        return "\n".join(lines)
    
    async def _arun(
        self,
        command: str,
        files: Optional[Dict[str, str]] = None,
        working_directory: str = "/workspace"
    ) -> str:
        """Async version - just calls sync version"""
        return self._run(command, files, working_directory)


# Standalone test
if __name__ == "__main__":
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        stream=sys.stdout
    )
    
    print("=" * 70)
    print("Testing Runtime Execution Tool")
    print("=" * 70)
    
    tool = RuntimeExecutionTool()
    
    # Test 1: Simple Python
    print("\n\nTest 1: Simple Python Command")
    print("-" * 70)
    result = tool._run(command="python3 -c 'print(\"Hello from Runtime!\")'")
    print(result)
    
    # Test 2: With test file (like Executor will use)
    print("\n\nTest 2: Run Test File (Like Executor)")
    print("-" * 70)
    
    test_code = """import pytest

def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 5 - 3 == 2
"""
    
    result = tool._run(
        command="python3 -m pytest test_example.py -v",
        files={"test_example.py": test_code}
    )
    print(result)
    
    # Test 3: With test + source file (like from KG)
    print("\n\nTest 3: Test + Source File (From Knowledge Graph)")
    print("-" * 70)
    
    source_code = """def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""
    
    test_code = """import pytest
from calculator import add, multiply

def test_add():
    assert add(2, 3) == 5

def test_multiply():
    assert multiply(4, 5) == 20
"""
    
    result = tool._run(
        command="python3 -m pytest test_calculator.py -v",
        files={
            "calculator.py": source_code,
            "test_calculator.py": test_code
        }
    )
    print(result)
    
    print("\n" + "=" * 70)
    print("✅ All tests complete! Tool is ready for Executor Agent.")
    print("=" * 70)