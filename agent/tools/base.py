from typing import Any, Dict, Optional, List, Literal
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import json
import base64

@dataclass
class ToolResult:
    '''Result from tool execution'''
    output: Optional[str] = None
    error: Optional[str] = None
    base64_image: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True

class BaseAnthropicTool(ABC):
    '''Base class for all tools'''
    
    name: str
    description: str
    
    @abstractmethod
    async def __call__(self, **kwargs) -> ToolResult:
        '''Execute the tool'''
        pass
    
    def to_params(self) -> Dict[str, Any]:
        '''Convert to Anthropic API parameters'''
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.get_input_schema()
        }
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        '''Get JSON schema for tool inputs'''
        pass

class ToolCollection:
    '''Collection of tools for the agent'''
    
    def __init__(self, *tools: BaseAnthropicTool):
        self.tools = {tool.name: tool for tool in tools}
    
    def get_tool(self, name: str) -> Optional[BaseAnthropicTool]:
        return self.tools.get(name)
    
    def to_params(self) -> List[Dict[str, Any]]:
        return [tool.to_params() for tool in self.tools.values()]
    
    async def execute(self, tool_name: str, **kwargs) -> ToolResult:
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                error=f"Tool {tool_name} not found",
                success=False
            )
        return await tool(**kwargs)
