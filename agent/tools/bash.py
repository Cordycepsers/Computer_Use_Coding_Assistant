import asyncio
import os
import subprocess
from typing import Literal, Optional, Dict, Any
from .base import BaseAnthropicTool, ToolResult

class BashTool(BaseAnthropicTool):
    '''Execute bash commands and shell operations'''
    
    name: Literal["bash"] = "bash"
    description = "Execute bash commands, run scripts, manage processes and system operations"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The bash command to execute"
                },
                "working_directory": {
                    "type": "string",
                    "description": "Working directory for the command"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30)"
                },
                "capture_output": {
                    "type": "boolean",
                    "description": "Whether to capture stdout/stderr (default: true)"
                },
                "environment": {
                    "type": "object",
                    "description": "Additional environment variables"
                }
            },
            "required": ["command"]
        }
    
    async def __call__(
        self,
        command: str,
        working_directory: Optional[str] = None,
        timeout: int = 30,
        capture_output: bool = True,
        environment: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> ToolResult:
        '''Execute bash command'''
        
        try:
            # Prepare environment
            env = os.environ.copy()
            if environment:
                env.update(environment)
            
            # Set working directory
            cwd = working_directory or os.getcwd()
            
            # Create subprocess
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
                cwd=cwd,
                env=env
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(),
                    timeout=timeout
                )
                
                stdout_text = stdout.decode() if stdout else ""
                stderr_text = stderr.decode() if stderr else ""
                
                return ToolResult(
                    output=stdout_text,
                    error=stderr_text if stderr_text else None,
                    success=proc.returncode == 0,
                    metadata={
                        "command": command,
                        "return_code": proc.returncode,
                        "working_directory": cwd,
                        "execution_time": timeout
                    }
                )
                
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
                return ToolResult(
                    error=f"Command timed out after {timeout} seconds",
                    success=False,
                    metadata={"command": command, "timeout": timeout}
                )
                
        except Exception as e:
            return ToolResult(
                error=f"Failed to execute command: {str(e)}",
                success=False,
                metadata={"command": command}
            )
