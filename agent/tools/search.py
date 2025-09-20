import asyncio
import re
from typing import Literal, Optional, Dict, Any
from .base import BaseAnthropicTool, ToolResult

class SearchTool(BaseAnthropicTool):
    '''Search through files and code'''
    
    name: Literal["search"] = "search"
    description = "Search for text, patterns, and code across files"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"},
                "path": {"type": "string"},
                "file_types": {"type": "array", "items": {"type": "string"}},
                "case_sensitive": {"type": "boolean"}
            },
            "required": ["pattern"]
        }
    
    async def __call__(self, pattern: str, path: str = ".", **kwargs) -> ToolResult:
        try:
            # Use ripgrep for fast searching
            proc = await asyncio.create_subprocess_shell(
                f"rg '{pattern}' {path}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            return ToolResult(
                output=stdout.decode(),
                error=stderr.decode() if stderr else None,
                success=proc.returncode == 0,
                metadata={"pattern": pattern, "path": path}
            )
        except Exception as e:
            return ToolResult(error=str(e), success=False)
