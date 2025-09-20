from typing import List
from .base import BaseWorkflow, WorkflowStep

class DebuggingWorkflow(BaseWorkflow):
    '''Workflow for debugging code issues'''
    
    def define_steps(self, **kwargs) -> List[WorkflowStep]:
        file_path = kwargs.get("file_path", "")
        error_message = kwargs.get("error_message", "")
        
        return [
            WorkflowStep(
                name="analyze_error",
                description="Analyze the error",
                tool="debugger",
                params={"action": "analyze_error", "error_message": error_message}
            ),
            WorkflowStep(
                name="read_code",
                description="Read the problematic code",
                tool="code_editor",
                params={"action": "read", "file_path": file_path},
                depends_on=["analyze_error"]
            )
        ]
