import os
import logging
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
import json

logger = logging.getLogger(__name__)

class CodingAgent:
    """Main AI coding assistant agent"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found")
        
        self.client = Anthropic(api_key=self.api_key)
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        return """You are an expert coding assistant with computer control capabilities.
        You can:
        1. Write, edit, and refactor code in any language
        2. Debug issues and fix errors
        3. Run tests and ensure code quality
        4. Use git for version control
        5. Navigate IDEs and development tools
        6. Execute terminal commands
        7. Control the computer screen, mouse, and keyboard
        
        Best Practices:
        - Always test code after making changes
        - Follow language-specific conventions
        - Write clean, maintainable code
        - Add appropriate error handling
        - Document complex logic
        """
    
    async def execute_task(self, task: str, context: Dict[str, Any] = None):
        """Execute a coding task"""
        try:
            messages = [{"role": "user", "content": task}]
            
            if context:
                messages[0]["content"] += f"\n\nContext: {json.dumps(context)}"
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system=self.system_prompt,
                messages=messages
            )
            
            result_text = response.content[0].text if response.content else "No response"
            
            logger.info(f"Task executed successfully: {task[:50]}...")
            
            return {
                "status": "success",
                "response": result_text,
                "task_summary": task[:100]
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "task_summary": task[:100]
            }
