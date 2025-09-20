from typing import List
from .base import BaseWorkflow, WorkflowStep

class CodeGenerationWorkflow(BaseWorkflow):
    '''Workflow for generating code'''
    
    def define_steps(self, **kwargs) -> List[WorkflowStep]:
        task = kwargs.get("task", "")
        output_path = kwargs.get("output_path", "generated_code.py")
        
        return [
            WorkflowStep(
                name="generate_code",
                description="Generate the code",
                tool="code_editor",
                params={"action": "create", "file_path": output_path, "content": f"# Generated code for: {task}"}
            ),
            WorkflowStep(
                name="format_code",
                description="Format the code",
                tool="bash",
                params={"command": f"black {output_path}"},
                depends_on=["generate_code"]
            )
        ]
