import os
import aiofiles
from typing import Literal, Optional, Dict, Any
from .base import BaseAnthropicTool, ToolResult

class CodeEditorTool(BaseAnthropicTool):
    '''Advanced code editing and manipulation tool'''
    
    name: Literal["code_editor"] = "code_editor"
    description = "Edit, analyze, and manipulate code files with advanced features"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read", "write", "create", "delete", "analyze", "search", "replace"]
                },
                "file_path": {"type": "string"},
                "content": {"type": "string"},
                "search_pattern": {"type": "string"},
                "replace_with": {"type": "string"}
            },
            "required": ["action"]
        }
    
    async def __call__(self, action: str, file_path: Optional[str] = None, 
                      content: Optional[str] = None, **kwargs) -> ToolResult:
        try:
            if action == "read" and file_path:
                async with aiofiles.open(file_path, 'r') as f:
                    content = await f.read()
                return ToolResult(output=content, metadata={"path": file_path})
            elif action == "write" and file_path and content is not None:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                async with aiofiles.open(file_path, 'w') as f:
                    await f.write(content)
                return ToolResult(output=f"File {file_path} written", metadata={"path": file_path})
            else:
                return ToolResult(error=f"Invalid action or missing parameters: {action}", success=False)
        except Exception as e:
            return ToolResult(error=str(e), success=False)
