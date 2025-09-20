import os
import shutil
from typing import Literal, Optional, Dict, Any
from .base import BaseAnthropicTool, ToolResult

class FileManagerTool(BaseAnthropicTool):
    '''Manage files and directories'''
    
    name: Literal["file_manager"] = "file_manager"
    description = "Create, copy, move, delete files and directories"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["copy", "move", "delete", "mkdir", "list"]},
                "source": {"type": "string"},
                "destination": {"type": "string"},
                "path": {"type": "string"}
            },
            "required": ["action"]
        }
    
    async def __call__(self, action: str, **kwargs) -> ToolResult:
        try:
            if action == "copy":
                source = kwargs["source"]
                destination = kwargs["destination"]
                shutil.copy2(source, destination)
                return ToolResult(output=f"Copied {source} to {destination}")
            elif action == "mkdir":
                path = kwargs["path"]
                os.makedirs(path, exist_ok=True)
                return ToolResult(output=f"Created directory {path}")
            elif action == "list":
                path = kwargs.get("path", ".")
                items = os.listdir(path)
                return ToolResult(output="\n".join(items), metadata={"items": items})
            else:
                return ToolResult(error=f"Unknown action: {action}", success=False)
        except Exception as e:
            return ToolResult(error=str(e), success=False)
