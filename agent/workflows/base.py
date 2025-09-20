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

@dataclass
class WorkflowResult:
    '''Result from workflow execution'''
    success: bool
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

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
        try:
            self.steps = self.define_steps(**kwargs)
            
            for step in self.steps:
                if self._check_dependencies(step):
                    result = await self._execute_step(step)
                    if result.get("success"):
                        self.results[step.name] = result.get("data")
                    else:
                        self.errors.append(f"Step {step.name} failed: {result.get('error')}")
            
            return WorkflowResult(
                success=len(self.errors) == 0,
                results=self.results,
                errors=self.errors
            )
        except Exception as e:
            return WorkflowResult(success=False, errors=[str(e)])
    
    def _check_dependencies(self, step: WorkflowStep) -> bool:
        '''Check if step dependencies are met'''
        return all(dep in self.results for dep in step.depends_on)
    
    async def _execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        '''Execute a single step'''
        try:
            result = await self.agent.tools.execute(step.tool, **step.params)
            return {"success": result.success, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
