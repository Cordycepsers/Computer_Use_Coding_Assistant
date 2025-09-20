import asyncio
from typing import Literal, Optional, Dict, Any
from .base import BaseAnthropicTool, ToolResult

class DebuggerTool(BaseAnthropicTool):
    '''Debug code issues and analyze errors'''
    
    name: Literal["debugger"] = "debugger"
    description = "Debug code, analyze errors, set breakpoints, and trace execution"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["analyze_error", "trace", "inspect"]},
                "file_path": {"type": "string"},
                "error_message": {"type": "string"},
                "stack_trace": {"type": "string"}
            },
            "required": ["action"]
        }
    
    async def __call__(self, action: str, **kwargs) -> ToolResult:
        try:
            if action == "analyze_error":
                error_msg = kwargs.get("error_message", "")
                return ToolResult(
                    output=f"Analyzed error: {error_msg}",
                    metadata={"action": action, "error": error_msg}
                )
            else:
                return ToolResult(error=f"Unknown action: {action}", success=False)
        except Exception as e:
            return ToolResult(error=str(e), success=False)
