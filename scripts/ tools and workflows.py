#!/usr/bin/env python3
"""
Complete Tools and Workflows Implementation for Computer Use Coding Assistant
This file should be added to the package generator script
"""

# =============================================================================
# TOOLS IMPLEMENTATION
# =============================================================================

# File: agent/tools/__init__.py
TOOLS_INIT = """
from .base import BaseAnthropicTool, ToolResult, ToolCollection
from .computer import ComputerTool
from .code_editor import CodeEditorTool
from .bash import BashTool
from .git import GitTool
from .debugger import DebuggerTool
from .test_runner import TestRunnerTool
from .file_manager import FileManagerTool
from .search import SearchTool
from .browser import BrowserTool
from .database import DatabaseTool

__all__ = [
    'BaseAnthropicTool',
    'ToolResult',
    'ToolCollection',
    'ComputerTool',
    'CodeEditorTool',
    'BashTool',
    'GitTool',
    'DebuggerTool',
    'TestRunnerTool',
    'FileManagerTool',
    'SearchTool',
    'BrowserTool',
    'DatabaseTool'
]
"""

# File: agent/tools/base.py
BASE_TOOL = """
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
"""

# File: agent/tools/computer.py
COMPUTER_TOOL = """
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
"""

# File: agent/tools/code_editor.py
CODE_EDITOR_TOOL = """
import os
import aiofiles
import ast
import re
from typing import Literal, Optional, List, Dict, Any
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
                    "enum": ["read", "write", "create", "delete", "analyze", 
                            "refactor", "format", "search", "replace", "insert_at_line"]
                },
                "file_path": {"type": "string"},
                "content": {"type": "string"},
                "line_number": {"type": "integer"},
                "search_pattern": {"type": "string"},
                "replace_with": {"type": "string"},
                "refactor_type": {
                    "type": "string",
                    "enum": ["extract_function", "rename_variable", "optimize_imports", 
                            "extract_constant", "inline_variable"]
                }
            },
            "required": ["action"]
        }
    
    async def __call__(
        self,
        action: str,
        file_path: Optional[str] = None,
        content: Optional[str] = None,
        line_number: Optional[int] = None,
        search_pattern: Optional[str] = None,
        replace_with: Optional[str] = None,
        refactor_type: Optional[str] = None,
        **kwargs
    ) -> ToolResult:
        '''Execute code editing action'''
        
        try:
            if action == "read" and file_path:
                return await self._read_file(file_path)
            elif action == "write" and file_path and content is not None:
                return await self._write_file(file_path, content)
            elif action == "create" and file_path:
                return await self._create_file(file_path, content or "")
            elif action == "delete" and file_path:
                return await self._delete_file(file_path)
            elif action == "analyze" and file_path:
                return await self._analyze_code(file_path)
            elif action == "refactor" and file_path and refactor_type:
                return await self._refactor_code(file_path, refactor_type, **kwargs)
            elif action == "format" and file_path:
                return await self._format_code(file_path)
            elif action == "search" and search_pattern:
                return await self._search_code(search_pattern, file_path)
            elif action == "replace" and file_path and search_pattern and replace_with is not None:
                return await self._replace_in_file(file_path, search_pattern, replace_with)
            elif action == "insert_at_line" and file_path and line_number and content:
                return await self._insert_at_line(file_path, line_number, content)
            else:
                return ToolResult(
                    error=f"Invalid action or missing parameters: {action}",
                    success=False
                )
        except Exception as e:
            return ToolResult(error=str(e), success=False)
    
    async def _read_file(self, path: str) -> ToolResult:
        '''Read file contents'''
        try:
            async with aiofiles.open(path, 'r') as f:
                content = await f.read()
            
            # Get file info
            lines = content.split('\\n')
            file_info = {
                "path": path,
                "lines": len(lines),
                "size": len(content),
                "language": self._detect_language(path)
            }
            
            return ToolResult(
                output=content,
                metadata=file_info
            )
        except Exception as e:
            return ToolResult(error=f"Failed to read {path}: {str(e)}", success=False)
    
    async def _write_file(self, path: str, content: str) -> ToolResult:
        '''Write content to file'''
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            async with aiofiles.open(path, 'w') as f:
                await f.write(content)
            
            return ToolResult(
                output=f"File {path} written successfully",
                metadata={"path": path, "size": len(content)}
            )
        except Exception as e:
            return ToolResult(error=f"Failed to write {path}: {str(e)}", success=False)
    
    async def _create_file(self, path: str, content: str) -> ToolResult:
        '''Create a new file'''
        if os.path.exists(path):
            return ToolResult(
                error=f"File {path} already exists",
                success=False
            )
        return await self._write_file(path, content)
    
    async def _delete_file(self, path: str) -> ToolResult:
        '''Delete a file'''
        try:
            os.remove(path)
            return ToolResult(output=f"File {path} deleted successfully")
        except Exception as e:
            return ToolResult(error=f"Failed to delete {path}: {str(e)}", success=False)
    
    async def _analyze_code(self, path: str) -> ToolResult:
        '''Analyze code structure and metrics'''
        try:
            async with aiofiles.open(path, 'r') as f:
                content = await f.read()
            
            language = self._detect_language(path)
            analysis = {
                "language": language,
                "lines": len(content.split('\\n')),
                "characters": len(content),
                "functions": [],
                "classes": [],
                "imports": []
            }
            
            if language == "python":
                analysis.update(self._analyze_python(content))
            elif language in ["javascript", "typescript"]:
                analysis.update(self._analyze_javascript(content))
            
            return ToolResult(
                output=f"Code analysis for {path}",
                metadata=analysis
            )
        except Exception as e:
            return ToolResult(error=f"Failed to analyze {path}: {str(e)}", success=False)
    
    async def _refactor_code(self, path: str, refactor_type: str, **kwargs) -> ToolResult:
        '''Perform code refactoring'''
        try:
            async with aiofiles.open(path, 'r') as f:
                content = await f.read()
            
            if refactor_type == "extract_function":
                refactored = await self._extract_function(content, **kwargs)
            elif refactor_type == "rename_variable":
                refactored = await self._rename_variable(content, **kwargs)
            elif refactor_type == "optimize_imports":
                refactored = await self._optimize_imports(content)
            elif refactor_type == "extract_constant":
                refactored = await self._extract_constant(content, **kwargs)
            elif refactor_type == "inline_variable":
                refactored = await self._inline_variable(content, **kwargs)
            else:
                return ToolResult(
                    error=f"Unknown refactor type: {refactor_type}",
                    success=False
                )
            
            await self._write_file(path, refactored)
            
            return ToolResult(
                output=f"Refactored {path} with {refactor_type}",
                metadata={"refactor_type": refactor_type, "path": path}
            )
        except Exception as e:
            return ToolResult(error=f"Refactoring failed: {str(e)}", success=False)
    
    async def _format_code(self, path: str) -> ToolResult:
        '''Format code according to language standards'''
        try:
            language = self._detect_language(path)
            
            if language == "python":
                proc = await asyncio.create_subprocess_exec(
                    "black", path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            elif language in ["javascript", "typescript"]:
                proc = await asyncio.create_subprocess_exec(
                    "prettier", "--write", path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            else:
                return ToolResult(
                    error=f"No formatter available for {language}",
                    success=False
                )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                return ToolResult(output=f"Formatted {path}")
            else:
                return ToolResult(error=stderr.decode(), success=False)
                
        except Exception as e:
            return ToolResult(error=f"Formatting failed: {str(e)}", success=False)
    
    async def _search_code(self, pattern: str, path: Optional[str] = None) -> ToolResult:
        '''Search for pattern in code'''
        try:
            if path:
                # Search in specific file
                async with aiofiles.open(path, 'r') as f:
                    content = await f.read()
                
                matches = []
                for i, line in enumerate(content.split('\\n'), 1):
                    if re.search(pattern, line):
                        matches.append({
                            "file": path,
                            "line": i,
                            "content": line.strip()
                        })
            else:
                # Search in workspace
                proc = await asyncio.create_subprocess_shell(
                    f"rg '{pattern}' --json",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                
                matches = []
                for line in stdout.decode().split('\\n'):
                    if line:
                        try:
                            match_data = json.loads(line)
                            if match_data.get('type') == 'match':
                                matches.append({
                                    "file": match_data['data']['path']['text'],
                                    "line": match_data['data']['line_number'],
                                    "content": match_data['data']['lines']['text'].strip()
                                })
                        except:
                            pass
            
            return ToolResult(
                output=f"Found {len(matches)} matches",
                metadata={"matches": matches, "pattern": pattern}
            )
        except Exception as e:
            return ToolResult(error=f"Search failed: {str(e)}", success=False)
    
    async def _replace_in_file(self, path: str, pattern: str, replacement: str) -> ToolResult:
        '''Replace pattern in file'''
        try:
            async with aiofiles.open(path, 'r') as f:
                content = await f.read()
            
            new_content, count = re.subn(pattern, replacement, content)
            
            if count > 0:
                await self._write_file(path, new_content)
                return ToolResult(
                    output=f"Replaced {count} occurrences in {path}",
                    metadata={"replacements": count, "pattern": pattern}
                )
            else:
                return ToolResult(
                    output=f"No matches found for {pattern} in {path}",
                    metadata={"replacements": 0}
                )
        except Exception as e:
            return ToolResult(error=f"Replace failed: {str(e)}", success=False)
    
    async def _insert_at_line(self, path: str, line_number: int, content: str) -> ToolResult:
        '''Insert content at specific line'''
        try:
            async with aiofiles.open(path, 'r') as f:
                lines = (await f.read()).split('\\n')
            
            if line_number > len(lines):
                line_number = len(lines)
            
            lines.insert(line_number - 1, content)
            
            await self._write_file(path, '\\n'.join(lines))
            
            return ToolResult(
                output=f"Inserted content at line {line_number} in {path}",
                metadata={"line": line_number, "path": path}
            )
        except Exception as e:
            return ToolResult(error=f"Insert failed: {str(e)}", success=False)
    
    def _detect_language(self, path: str) -> str:
        '''Detect programming language from file extension'''
        ext = os.path.splitext(path)[1].lower()
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.m': 'matlab',
            '.jl': 'julia'
        }
        return language_map.get(ext, 'unknown')
    
    def _analyze_python(self, content: str) -> Dict[str, Any]:
        '''Analyze Python code'''
        try:
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.append(node.module or '')
            
            return {
                "functions": functions,
                "classes": classes,
                "imports": list(set(imports))
            }
        except:
            return {}
    
    def _analyze_javascript(self, content: str) -> Dict[str, Any]:
        '''Analyze JavaScript/TypeScript code'''
        # Simple regex-based analysis
        functions = re.findall(r'function\\s+(\\w+)\\s*\\(', content)
        arrow_functions = re.findall(r'const\\s+(\\w+)\\s*=\\s*\\([^)]*\\)\\s*=>', content)
        classes = re.findall(r'class\\s+(\\w+)', content)
        imports = re.findall(r'import\\s+.*\\s+from\\s+[\'"]([^\'"]+)[\'"]', content)
        
        return {
            "functions": functions + arrow_functions,
            "classes": classes,
            "imports": imports
        }
    
    async def _extract_function(self, content: str, start_line: int, end_line: int, function_name: str) -> str:
        '''Extract code into a function'''
        lines = content.split('\\n')
        extracted_lines = lines[start_line-1:end_line]
        
        # Create function
        function_def = f"def {function_name}():\\n"
        function_body = '\\n'.join(f"    {line}" for line in extracted_lines)
        function = function_def + function_body
        
        # Replace original lines with function call
        lines[start_line-1:end_line] = [f"{function_name}()"]
        
        # Add function definition before first use
        lines.insert(start_line-2, function)
        
        return '\\n'.join(lines)
    
    async def _rename_variable(self, content: str, old_name: str, new_name: str) -> str:
        '''Rename a variable throughout the code'''
        # Simple word boundary replacement
        pattern = r'\\b' + re.escape(old_name) + r'\\b'
        return re.sub(pattern, new_name, content)
    
    async def _optimize_imports(self, content: str) -> str:
        '''Optimize and sort imports'''
        lines = content.split('\\n')
        imports = []
        other_lines = []
        
        for line in lines:
            if line.startswith(('import ', 'from ')):
                imports.append(line)
            else:
                other_lines.append(line)
        
        # Sort imports
        imports.sort()
        
        # Remove duplicates
        imports = list(dict.fromkeys(imports))
        
        # Reconstruct file
        return '\\n'.join(imports + [''] + other_lines)
    
    async def _extract_constant(self, content: str, value: str, constant_name: str) -> str:
        '''Extract a value into a constant'''
        # Add constant definition at top
        lines = content.split('\\n')
        
        # Find first non-import line
        insert_index = 0
        for i, line in enumerate(lines):
            if not line.startswith(('import ', 'from ', '#')) and line.strip():
                insert_index = i
                break
        
        # Insert constant definition
        lines.insert(insert_index, f"{constant_name} = {value}")
        
        # Replace all occurrences of the value
        content = '\\n'.join(lines)
        return content.replace(value, constant_name)
    
    async def _inline_variable(self, content: str, variable_name: str) -> str:
        '''Inline a variable (replace variable with its value)'''
        # Find variable definition
        pattern = f"{variable_name}\\s*=\\s*(.+)"
        match = re.search(pattern, content)
        
        if match:
            value = match.group(1)
            # Remove variable definition
            content = re.sub(pattern + '\\n', '', content)
            # Replace all uses with value
            content = re.sub(r'\\b' + variable_name + r'\\b', value, content)
        
        return content
"""

# File: agent/tools/git.py
GIT_TOOL = """
import asyncio
from typing import Literal, Optional, List
from .base import BaseAnthropicTool, ToolResult

class GitTool(BaseAnthropicTool):
    '''Git version control operations'''
    
    name: Literal["git"] = "git"
    description = "Perform git operations - status, diff, commit, push, pull, branch, merge, etc."
    
    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "diff", "add", "commit", "push", "pull", 
                            "branch", "checkout", "merge", "stash", "log", "reset",
                            "rebase", "cherry_pick", "tag", "remote"]
                },
                "message": {"type": "string", "description": "Commit message"},
                "branch": {"type": "string", "description": "Branch name"},
                "files": {"type": "array", "items": {"type": "string"}},
                "remote": {"type": "string", "description": "Remote name"},
                "options": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["action"]
        }
    
    async def __call__(
        self,
        action: str,
        message: Optional[str] = None,
        branch: Optional[str] = None,
        files: Optional[List[str]] = None,
        remote: Optional[str] = None,
        options: Optional[List[str]] = None,
        **kwargs
    ) -> ToolResult:
        '''Execute git operation'''
        
        try:
            if action == "status":
                return await self._git_status()
            elif action == "diff":
                return await self._git_diff(files)
            elif action == "add":
                return await self._git_add(files or ["."])
            elif action == "commit" and message:
                return await self._git_commit(message)
            elif action == "push":
                return await self._git_push(remote or "origin", branch)
            elif action == "pull":
                return await self._git_pull(remote or "origin", branch)
            elif action == "branch":
                return await self._git_branch(branch)
            elif action == "checkout":
                return await self._git_checkout(branch)
            elif action == "merge" and branch:
                return await self._git_merge(branch)
            elif action == "stash":
                return await self._git_stash(kwargs.get("stash_action", "push"))
            elif action == "log":
                return await self._git_log(kwargs.get("limit", 10))
            elif action == "reset":
                return await self._git_reset(kwargs.get("mode", "mixed"), kwargs.get("commit", "HEAD"))
            elif action == "rebase" and branch:
                return await self._git_rebase(branch)
            elif action == "cherry_pick" and kwargs.get("commit"):
                return await self._git_cherry_pick(kwargs["commit"])
            elif action == "tag":
                return await self._git_tag(kwargs.get("tag_name"), message)
            elif action == "remote":
                return await self._git_remote(kwargs.get("remote_action", "list"))
            else:
                return ToolResult(
                    error=f"Invalid git action or missing parameters: {action}",
                    success=False
                )
        except Exception as e:
            return ToolResult(error=str(e), success=False)
    
    async def _run_git(self, command: str) -> tuple[str, str, int]:
        '''Run a git command'''
        proc = await asyncio.create_subprocess_shell(
            f"git {command}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode(), stderr.decode(), proc.returncode
    
    async def _git_status(self) -> ToolResult:
        '''Get git status'''
        stdout, stderr, code = await self._run_git("status --porcelain")
        
        if code == 0:
            # Parse status output
            files = []
            for line in stdout.strip().split('\n'):
                if line:
                    status = line[:2]
                    filename = line[3:]
                    files.append({"status": status, "file": filename})
            
            # Get branch info
            branch_out, _, _ = await self._run_git("branch --show-current")
            current_branch = branch_out.strip()
            
            return ToolResult(
                output=f"On branch {current_branch}",
                metadata={"branch": current_branch, "files": files}
            )
        return ToolResult(error=stderr, success=False)
    
    async def _git_diff(self, files: Optional[List[str]] = None) -> ToolResult:
        '''Show git diff'''
        cmd = "diff"
        if files:
            cmd += " " + " ".join(files)
        
        stdout, stderr, code = await self._run_git(cmd)
        
        if code == 0:
            return ToolResult(output=stdout or "No changes")
        return ToolResult(error=stderr, success=False)
    
    async def _git_add(self, files: List[str]) -> ToolResult:
        '''Stage files'''
        cmd = "add " + " ".join(files)
        stdout, stderr, code = await self._run_git(cmd)
        
        if code == 0:
            return ToolResult(output=f"Staged {len(files)} file(s)")
        return ToolResult(error=stderr, success=False)
    
    async def _git_commit(self, message: str) -> ToolResult:
        '''Create a commit'''
        # Escape message
        message = message.replace('"', '\\"')
        stdout, stderr, code = await self._run_git(f'commit -m "{message}"')
        
        if code == 0:
            # Get commit hash
            hash_out, _, _ = await self._run_git("rev-parse HEAD")
            commit_hash = hash_out.strip()[:7]
            
            return ToolResult(
                output=f"Committed with hash {commit_hash}",
                metadata={"commit": commit_hash, "message": message}
            )
        return ToolResult(error=stderr, success=False)
    
    async def _git_push(self, remote: str, branch: Optional[str] = None) -> ToolResult:
        '''Push to remote'''
        cmd = f"push {remote}"
        if branch:
            cmd += f" {branch}"
        
        stdout, stderr, code = await self._run_git(cmd)
        
        if code == 0:
            return ToolResult(output=f"Pushed to {remote}/{branch or 'current branch'}")
        return ToolResult(error=stderr, success=False)
    
    async def _git_pull(self, remote: str, branch: Optional[str] = None) -> ToolResult:
        '''Pull from remote'''
        cmd = f"pull {remote}"
        if branch:
            cmd += f" {branch}"
        
        stdout, stderr, code = await self._run_git(cmd)
        
        if code == 0:
            return ToolResult(output=stdout or f"Pulled from {remote}")
        return ToolResult(error=stderr, success=False)
    
    async def _git_branch(self, branch: Optional[str] = None) -> ToolResult:
        '''Create or list branches'''
        if branch:
            stdout, stderr, code = await self._run_git(f"branch {branch}")
            if code == 0:
                return ToolResult(output=f"Created branch {branch}")
            return ToolResult(error=stderr, success=False)
        else:
            stdout, stderr, code = await self._run_git("branch")
            if code == 0:
                branches = [line.strip() for line in stdout.strip().split('\n')]
                current = next((b[2:] for b in branches if b.startswith('*')), None)
                all_branches = [b.lstrip('* ') for b in branches]
                
                return ToolResult(
                    output=stdout,
                    metadata={"current": current, "branches": all_branches}
                )
            return ToolResult(error=stderr, success=False)
    
    async def _git_checkout(self, branch: str) -> ToolResult:
        '''Switch branches'''
        stdout, stderr, code = await self._run_git(f"checkout {branch}")
        
        if code == 0:
            return ToolResult(output=f"Switched to branch {branch}")
        
        # Try creating and checking out new branch
        stdout, stderr, code = await self._run_git(f"checkout -b {branch}")
        if code == 0:
            return ToolResult(output=f"Created and switched to new branch {branch}")
        
        return ToolResult(error=stderr, success=False)
    
    async def _git_merge(self, branch: str) -> ToolResult:
        '''Merge branch'''
        stdout, stderr, code = await self._run_git(f"merge {branch}")
        
        if code == 0:
            return ToolResult(output=f"Merged {branch}" + (f"\n{stdout}" if stdout else ""))
        return ToolResult(error=stderr, success=False)
    
    async def _git_stash(self, action: str = "push") -> ToolResult:
        '''Stash changes'''
        stdout, stderr, code = await self._run_git(f"stash {action}")
        
        if code == 0:
            return ToolResult(output=stdout or f"Stash {action} completed")
        return ToolResult(error=stderr, success=False)
    
    async def _git_log(self, limit: int = 10) -> ToolResult:
        '''Show commit log'''
        cmd = f"log --oneline -n {limit}"
        stdout, stderr, code = await self._run_git(cmd)
        
        if code == 0:
            commits = []
            for line in stdout.strip().split('\n'):
                if line:
                    parts = line.split(' ', 1)
                    commits.append({
                        "hash": parts[0],
                        "message": parts[1] if len(parts) > 1 else ""
                    })
            
            return ToolResult(
                output=stdout,
                metadata={"commits": commits}
            )
        return ToolResult(error=stderr, success=False)
    
    async def _git_reset(self, mode: str, commit: str) -> ToolResult:
        '''Reset to commit'''
        stdout, stderr, code = await self._run_git(f"reset --{mode} {commit}")
        
        if code == 0:
            return ToolResult(output=f"Reset to {commit} with mode {mode}")
        return ToolResult(error=stderr, success=False)
    
    async def _git_rebase(self, branch: str) -> ToolResult:
        '''Rebase on branch'''
        stdout, stderr, code = await self._run_git(f"rebase {branch}")
        
        if code == 0:
            return ToolResult(output=f"Rebased on {branch}")
        return ToolResult(error=stderr, success=False)
    
    async def _git_cherry_pick(self, commit: str) -> ToolResult:
        '''Cherry-pick commit'''
        stdout, stderr, code = await self._run_git(f"cherry-pick {commit}")
        
        if code == 0:
            return ToolResult(output=f"Cherry-picked {commit}")
        return ToolResult(error=stderr, success=False)
    
    async def _git_tag(self, tag_name: Optional[str] = None, message: Optional[str] = None) -> ToolResult:
        '''Create or list tags'''
        if tag_name:
            cmd = f"tag {tag_name}"
            if message:
                cmd += f' -m "{message}"'
            
            stdout, stderr, code = await self._run_git(cmd)
            if code == 0:
                return ToolResult(output=f"Created tag {tag_name}")
            return ToolResult(error=stderr, success=False)
        else:
            stdout, stderr, code = await self._run_git("tag")
            if code == 0:
                tags = stdout.strip().split('\n') if stdout.strip() else []
                return ToolResult(
                    output=stdout or "No tags",
                    metadata={"tags": tags}
                )
            return ToolResult(error=stderr, success=False)
    
    async def _git_remote(self, action: str = "list") -> ToolResult:
        '''Manage remotes'''
        if action == "list":
            stdout, stderr, code = await self._run_git("remote -v")
            if code == 0:
                return ToolResult(output=stdout or "No remotes")
            return ToolResult(error=stderr, success=False)
        
        return ToolResult(error=f"Unknown remote action: {action}", success=False)
"""

# =============================================================================
# WORKFLOWS IMPLEMENTATION
# =============================================================================

# File: agent/workflows/__init__.py
WORKFLOWS_INIT = """
from .base import BaseWorkflow, WorkflowResult
from .code_generation import CodeGenerationWorkflow
from .debugging import DebuggingWorkflow
from .refactoring import RefactoringWorkflow
from .testing import TestingWorkflow
from .documentation import DocumentationWorkflow
from .review import CodeReviewWorkflow
from .deployment import DeploymentWorkflow
from .optimization import OptimizationWorkflow

__all__ = [
    'BaseWorkflow',
    'WorkflowResult',
    'CodeGenerationWorkflow',
    'DebuggingWorkflow',
    'RefactoringWorkflow',
    'TestingWorkflow',
    'DocumentationWorkflow',
    'CodeReviewWorkflow',
    'DeploymentWorkflow',
    'OptimizationWorkflow'
]
"""

# File: agent/workflows/base.py
WORKFLOW_BASE = """
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class WorkflowStep:
    '''Individual step in a workflow'''
    name: str
    description: str
    tool: str
    params: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)
    retry_count: int = 3
    timeout: Optional[int] = None

@dataclass
class WorkflowResult:
    '''Result from workflow execution'''
    success: bool
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[float] = None

class BaseWorkflow(ABC):
    '''Base class for all workflows'''
    
    def __init__(self, agent):
        self.agent = agent
        self.steps: List[WorkflowStep] = []
        self.results: Dict[str, Any] = {}
        self.errors: List[str] = []
    
    @abstractmethod
    def define_steps(self, **kwargs) -> List[WorkflowStep]:
        '''Define workflow steps'''
        pass
    
    async def execute(self, **kwargs) -> WorkflowResult:
        '''Execute the workflow'''
        import time
        start_time = time.time()
        
        try:
            # Define steps
            self.steps = self.define_steps(**kwargs)
            
            # Execute steps
            for step in self.steps:
                # Check dependencies
                if not self._check_dependencies(step):
                    self.errors.append(f"Dependencies not met for {step.name}")
                    continue
                
                # Execute step with retries
                result = await self._execute_step(step)
                
                if result.get("success"):
                    self.results[step.name] = result.get("data")
                    logger.info(f"Step {step.name} completed successfully")
                else:
                    self.errors.append(f"Step {step.name} failed: {result.get('error')}")
                    
                    # Check if step is critical
                    if step.name.startswith("critical_"):
                        logger.error(f"Critical step {step.name} failed, aborting workflow")
                        break
            
            duration = time.time() - start_time
            
            return WorkflowResult(
                success=len(self.errors) == 0,
                results=self.results,
                errors=self.errors,
                metadata={"steps": len(self.steps), "completed": len(self.results)},
                duration=duration
            )
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            return WorkflowResult(
                success=False,
                errors=[str(e)],
                duration=time.time() - start_time
            )
    
    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        '''Execute a single step with retries'''
        for attempt in range(step.retry_count):
            try:
                # Execute with timeout if specified
                if step.timeout:
                    result = await asyncio.wait_for(
                        self.agent.tools.execute(step.tool, **step.params),
                        timeout=step.timeout
                    )
                else:
                    result = await self.agent.tools.execute(step.tool, **step.params)
                
                if result.success:
                    return {"success": True, "data": result}
                
                # Retry on failure
                if attempt < step.retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                
                return {"success": False, "error": result.error}
                
            except asyncio.TimeoutError:
                return {"success": False, "error": f"Step timed out after {step.timeout}s"}
            except Exception as e:
                if attempt < step.retry_count - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return {"success": False, "error": str(e)}
        
        return {"success": False, "error": "Max retries exceeded"}
    
    def _check_dependencies(self, step: WorkflowStep) -> bool:
        '''Check if step dependencies are met'''
        for dep in step.depends_on:
            if dep not in self.results:
                return False
        return True
    
    async def rollback(self):
        '''Rollback workflow changes on failure'''
        logger.info("Rolling back workflow changes...")
        # Implement rollback logic
        pass
"""

# File: agent/workflows/code_generation.py
CODE_GENERATION_WORKFLOW = """
from typing import Dict, Any, List
from .base import BaseWorkflow, WorkflowStep, WorkflowResult

class CodeGenerationWorkflow(BaseWorkflow):
    '''Workflow for generating code'''
    
    def define_steps(self, **kwargs) -> List[WorkflowStep]:
        task = kwargs.get("task", "")
        language = kwargs.get("language", "python")
        framework = kwargs.get("framework", "")
        output_path = kwargs.get("output_path", f"generated_code.{self._get_extension(language)}")
        
        steps = [
            WorkflowStep(
                name="analyze_requirements",
                description="Analyze the task requirements",
                tool="code_editor",
                params={
                    "action": "analyze",
                    "file_path": "requirements.txt"
                }
            ),
            
            WorkflowStep(
                name="generate_structure",
                description="Generate project structure",
                tool="bash",
                params={
                    "command": f"mkdir -p {os.path.dirname(output_path)}"
                }
            ),
            
            WorkflowStep(
                name="critical_generate_code",
                description="Generate the code",
                tool="agent",
                params={
                    "task": f"Generate {language} code: {task}",
                    "context": {"language": language, "framework": framework}
                },
                depends_on=["generate_structure"]
            ),
            
            WorkflowStep(
                name="write_code",
                description="Write generated code to file",
                tool="code_editor",
                params={
                    "action": "write",
                    "file_path": output_path,
                    "content": "{generated_code}"  # Will be filled from previous step
                },
                depends_on=["critical_generate_code"]
            ),
            
            WorkflowStep(
                name="format_code",
                description="Format the generated code",
                tool="code_editor",
                params={
                    "action": "format",
                    "file_path": output_path
                },
                depends_on=["write_code"]
            ),
            
            WorkflowStep(
                name="validate_syntax",
                description="Validate code syntax",
                tool="bash",
                params={
                    "command": self._get_validation_command(language, output_path)
                },
                depends_on=["format_code"]
            ),
            
            WorkflowStep(
                name="generate_tests",
                description="Generate basic tests",
                tool="agent",
                params={
                    "task": f"Generate unit tests for the code in {output_path}",
                    "context": {"language": language, "framework": framework}
                },
                depends_on=["validate_syntax"]
            ),
            
            WorkflowStep(
                name="create_documentation",
                description="Generate documentation",
                tool="agent",
                params={
                    "task": f"Generate documentation for {output_path}",
                    "context": {"format": "markdown"}
                },
                depends_on=["validate_syntax"]
            )
        ]
        
        return steps
    
    def _get_extension(self, language: str) -> str:
        '''Get file extension for language'''
        extensions = {
            "python": "py",
            "javascript": "js",
            "typescript": "ts",
            "java": "java",
            "go": "go",
            "rust": "rs",
            "cpp": "cpp",
            "c": "c",
            "ruby": "rb",
            "php": "php"
        }
        return extensions.get(language.lower(), "txt")
    
    def _get_validation_command(self, language: str, file_path: str) -> str:
        '''Get syntax validation command for language'''
        commands = {
            "python": f"python3 -m py_compile {file_path}",
            "javascript": f"node --check {file_path}",
            "typescript": f"tsc --noEmit {file_path}",
            "java": f"javac -Xlint {file_path}",
            "go": f"go fmt {file_path}",
            "rust": f"rustc --edition 2021 --crate-type lib {file_path}",
            "ruby": f"ruby -c {file_path}"
        }
        return commands.get(language.lower(), "echo 'No validator available'")
"""

# File: agent/workflows/debugging.py
DEBUGGING_WORKFLOW = """
from typing import Dict, Any, List, Optional
from .base import BaseWorkflow, WorkflowStep, WorkflowResult

class DebuggingWorkflow(BaseWorkflow):
    '''Workflow for debugging code issues'''
    
    def define_steps(self, **kwargs) -> List[WorkflowStep]:
        error_message = kwargs.get("error_message", "")
        file_path = kwargs.get("file_path", "")
        stack_trace = kwargs.get("stack_trace", "")
        
        steps = [
            WorkflowStep(
                name="capture_error_context",
                description="Capture error context and environment",
                tool="bash",
                params={
                    "command": "env | grep -E '(PATH|PYTHON|NODE|JAVA)'"
                }
            ),
            
            WorkflowStep(
                name="analyze_error",
                description="Analyze the error message and stack trace",
                tool="agent",
                params={
                    "task": f"Analyze this error: {error_message}\nStack trace: {stack_trace}",
                    "context": {"type": "error_analysis"}
                }
            ),
            
            WorkflowStep(
                name="read_problematic_code",
                description="Read the problematic code file",
                tool="code_editor",
                params={
                    "action": "read",
                    "file_path": file_path
                },
                depends_on=["analyze_error"]
            ),
            
            WorkflowStep(
                name="identify_issue_location",
                description="Identify exact location of the issue",
                tool="code_editor",
                params={
                    "action": "search",
                    "file_path": file_path,
                    "search_pattern": "{error_pattern}"  # Derived from error analysis
                },
                depends_on=["read_problematic_code"]
            ),
            
            WorkflowStep(
                name="critical_generate_fix",
                description="Generate fix for the issue",
                tool="agent",
                params={
                    "task": "Generate a fix for the identified issue",
                    "context": {"error": error_message, "code": "{problematic_code}"}
                },
                depends_on=["identify_issue_location"]
            ),
            
            WorkflowStep(
                name="apply_fix",
                description="Apply the fix to the code",
                tool="code_editor",
                params={
                    "action": "replace",
                    "file_path": file_path,
                    "search_pattern": "{buggy_code}",
                    "replace_with": "{fixed_code}"
                },
                depends_on=["critical_generate_fix"]
            ),
            
            WorkflowStep(
                name="verify_fix",
                description="Verify the fix resolves the issue",
                tool="bash",
                params={
                    "command": f"python3 {file_path}"  # Or appropriate test command
                },
                depends_on=["apply_fix"],
                retry_count=1
            ),
            
            WorkflowStep(
                name="run_tests",
                description="Run tests to ensure no regression",
                tool="test_runner",
                params={
                    "action": "run",
                    "test_file": f"test_{os.path.basename(file_path)}"
                },
                depends_on=["verify_fix"]
            ),
            
            WorkflowStep(
                name="document_fix",
                description="Document the fix and root cause",
                tool="code_editor",
                params={
                    "action": "create",
                    "file_path": f"debug_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    "content": "{debug_report}"
                },
                depends_on=["verify_fix"]
            )
        ]
        
        return steps
    
    async def execute(self, **kwargs) -> WorkflowResult:
        '''Execute debugging workflow with enhanced error handling'''
        # Add debugging-specific setup
        logger.info(f"Starting debugging workflow for: {kwargs.get('error_message', 'Unknown error')}")
        
        # Create backup before making changes
        if file_path := kwargs.get("file_path"):
            await self._create_backup(file_path)
        
        # Execute base workflow
        result = await super().execute(**kwargs)
        
        # If fix failed, restore backup
        if not result.success and file_path:
            await self._restore_backup(file_path)
        
        return result
    
    async def _create_backup(self, file_path: str):
        '''Create backup of file before debugging'''
        backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        await self.agent.tools.execute(
            "bash",
            command=f"cp {file_path} {backup_path}"
        )
        logger.info(f"Created backup: {backup_path}")
    
    async def _restore_backup(self, file_path: str):
        '''Restore backup if debugging fails'''
        # Find most recent backup
        result = await self.agent.tools.execute(
            "bash",
            command=f"ls -t {file_path}.backup.* 2>/dev/null | head -1"
        )
        
        if result.success and result.output:
            backup_path = result.output.strip()
            await self.agent.tools.execute(
                "bash",
                command=f"cp {backup_path} {file_path}"
            )
            logger.info(f"Restored backup from: {backup_path}")
"""

# Add this to the package generator script after the monitoring section
TOOLS_AND_WORKFLOWS_SECTION = """
# =============================================================================
# Create Tools and Workflows
# =============================================================================

print_status "Creating advanced tools and workflows..."

# Create all tool files
cat > ${PACKAGE_DIR}/agent/tools/__init__.py << 'EOF'
{TOOLS_INIT}
EOF

cat > ${PACKAGE_DIR}/agent/tools/base.py << 'EOF'
{BASE_TOOL}
EOF

cat > ${PACKAGE_DIR}/agent/tools/computer.py << 'EOF'
{COMPUTER_TOOL}
EOF

cat > ${PACKAGE_DIR}/agent/tools/code_editor.py << 'EOF'
{CODE_EDITOR_TOOL}
EOF

cat > ${PACKAGE_DIR}/agent/tools/git.py << 'EOF'
{GIT_TOOL}
EOF

# Create all workflow files
cat > ${PACKAGE_DIR}/agent/workflows/__init__.py << 'EOF'
{WORKFLOWS_INIT}
EOF

cat > ${PACKAGE_DIR}/agent/workflows/base.py << 'EOF'
{WORKFLOW_BASE}
EOF

cat > ${PACKAGE_DIR}/agent/workflows/code_generation.py << 'EOF'
{CODE_GENERATION_WORKFLOW}
EOF

cat > ${PACKAGE_DIR}/agent/workflows/debugging.py << 'EOF'
{DEBUGGING_WORKFLOW}
EOF

print_status "Tools and workflows created successfully"
"""