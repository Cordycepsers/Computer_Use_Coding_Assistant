import asyncio
import subprocess
import base64
from typing import Literal, Optional, Tuple
from .base import BaseAnthropicTool, ToolResult

class ComputerTool(BaseAnthropicTool):
    '''Control computer screen, mouse, and keyboard'''
    
    name: Literal["computer"] = "computer"
    description = "Control the computer - take screenshots, move mouse, click, type text, press keys"
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["screenshot", "click", "double_click", "right_click", 
                            "type", "key", "scroll", "drag", "mouse_move"]
                },
                "coordinate": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "[x, y] coordinates for mouse actions"
                },
                "text": {
                    "type": "string",
                    "description": "Text to type or key to press"
                },
                "direction": {
                    "type": "string",
                    "enum": ["up", "down", "left", "right"],
                    "description": "Scroll direction"
                },
                "amount": {
                    "type": "integer",
                    "description": "Scroll amount"
                }
            },
            "required": ["action"]
        }
    
    async def __call__(
        self,
        action: str,
        coordinate: Optional[Tuple[int, int]] = None,
        text: Optional[str] = None,
        direction: Optional[str] = None,
        amount: Optional[int] = None,
        **kwargs
    ) -> ToolResult:
        '''Execute computer control action'''
        
        try:
            if action == "screenshot":
                return await self._take_screenshot()
            elif action == "click" and coordinate:
                return await self._click(coordinate[0], coordinate[1])
            elif action == "double_click" and coordinate:
                return await self._double_click(coordinate[0], coordinate[1])
            elif action == "right_click" and coordinate:
                return await self._right_click(coordinate[0], coordinate[1])
            elif action == "type" and text:
                return await self._type_text(text)
            elif action == "key" and text:
                return await self._press_key(text)
            elif action == "scroll" and direction:
                return await self._scroll(direction, amount or 3)
            elif action == "drag" and coordinate and "end_coordinate" in kwargs:
                end = kwargs["end_coordinate"]
                return await self._drag(coordinate[0], coordinate[1], end[0], end[1])
            elif action == "mouse_move" and coordinate:
                return await self._mouse_move(coordinate[0], coordinate[1])
            else:
                return ToolResult(
                    error=f"Invalid action or missing parameters: {action}",
                    success=False
                )
        except Exception as e:
            return ToolResult(error=str(e), success=False)
    
    async def _take_screenshot(self) -> ToolResult:
        '''Take a screenshot of the current screen'''
        proc = await asyncio.create_subprocess_exec(
            "scrot", "-", 
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if proc.returncode == 0:
            return ToolResult(
                base64_image=base64.b64encode(stdout).decode(),
                metadata={"action": "screenshot"}
            )
        return ToolResult(error=stderr.decode(), success=False)
    
    async def _click(self, x: int, y: int) -> ToolResult:
        '''Click at coordinates'''
        await self._run_xdotool(f"mousemove {x} {y} click 1")
        return ToolResult(
            output=f"Clicked at ({x}, {y})",
            metadata={"action": "click", "x": x, "y": y}
        )
    
    async def _double_click(self, x: int, y: int) -> ToolResult:
        '''Double click at coordinates'''
        await self._run_xdotool(f"mousemove {x} {y} click --repeat 2 --delay 100 1")
        return ToolResult(
            output=f"Double clicked at ({x}, {y})",
            metadata={"action": "double_click", "x": x, "y": y}
        )
    
    async def _right_click(self, x: int, y: int) -> ToolResult:
        '''Right click at coordinates'''
        await self._run_xdotool(f"mousemove {x} {y} click 3")
        return ToolResult(
            output=f"Right clicked at ({x}, {y})",
            metadata={"action": "right_click", "x": x, "y": y}
        )
    
    async def _type_text(self, text: str) -> ToolResult:
        '''Type text'''
        # Escape special characters
        text = text.replace('"', '\\"').replace("'", "\\'")
        await self._run_xdotool(f'type "{text}"')
        return ToolResult(
            output=f"Typed: {text[:50]}..." if len(text) > 50 else f"Typed: {text}",
            metadata={"action": "type", "text_length": len(text)}
        )
    
    async def _press_key(self, key: str) -> ToolResult:
        '''Press a key or key combination'''
        await self._run_xdotool(f"key {key}")
        return ToolResult(
            output=f"Pressed key: {key}",
            metadata={"action": "key", "key": key}
        )
    
    async def _scroll(self, direction: str, amount: int) -> ToolResult:
        '''Scroll in a direction'''
        button_map = {"up": 4, "down": 5, "left": 6, "right": 7}
        button = button_map.get(direction, 5)
        
        for _ in range(amount):
            await self._run_xdotool(f"click {button}")
            await asyncio.sleep(0.1)
        
        return ToolResult(
            output=f"Scrolled {direction} {amount} times",
            metadata={"action": "scroll", "direction": direction, "amount": amount}
        )
    
    async def _drag(self, x1: int, y1: int, x2: int, y2: int) -> ToolResult:
        '''Drag from one point to another'''
        await self._run_xdotool(
            f"mousemove {x1} {y1} mousedown 1 mousemove {x2} {y2} mouseup 1"
        )
        return ToolResult(
            output=f"Dragged from ({x1}, {y1}) to ({x2}, {y2})",
            metadata={"action": "drag", "start": [x1, y1], "end": [x2, y2]}
        )
    
    async def _mouse_move(self, x: int, y: int) -> ToolResult:
        '''Move mouse to coordinates'''
        await self._run_xdotool(f"mousemove {x} {y}")
        return ToolResult(
            output=f"Moved mouse to ({x}, {y})",
            metadata={"action": "mouse_move", "x": x, "y": y}
        )
    
    async def _run_xdotool(self, command: str):
        '''Run xdotool command'''
        proc = await asyncio.create_subprocess_shell(
            f"xdotool {command}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await proc.communicate()
