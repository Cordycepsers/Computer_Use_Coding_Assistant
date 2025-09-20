import asyncio
from typing import Literal, Optional, Dict, Any, List
from .base import BaseAnthropicTool, ToolResult

class TestRunnerTool(BaseAnthropicTool):
    '''Run and manage tests'''
    
    name: Literal["test_runner"] = "test_runner"
    description = "Run tests, generate test reports, and manage test suites"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["run", "create", "discover"]},
                "test_file": {"type": "string"},
                "test_framework": {"type": "string"},
                "test_pattern": {"type": "string"}
            },
            "required": ["action"]
        }
    
    async def __call__(self, action: str, **kwargs) -> ToolResult:
        try:
            if action == "run":
                test_file = kwargs.get("test_file", "")
                proc = await asyncio.create_subprocess_shell(
                    f"python -m pytest {test_file}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                return ToolResult(
                    output=stdout.decode(),
                    error=stderr.decode() if stderr else None,
                    success=proc.returncode == 0,
                    metadata={"test_file": test_file}
                )
            else:
                return ToolResult(error=f"Unknown action: {action}", success=False)
        except Exception as e:
            return ToolResult(error=str(e), success=False)
