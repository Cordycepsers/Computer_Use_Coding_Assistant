import asyncio
from typing import Literal, Optional, List, Dict, Any
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
