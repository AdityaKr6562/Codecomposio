import typing as t
from abc import ABC, abstractmethod
from pathlib import Path

from pydantic import BaseModel, Field

from composio.core.local import Action
from composio.local_tools.local_workspace.commons import get_logger
from composio.workspace.base_workspace import Workspace
from composio.workspace.workspace_factory import WorkspaceFactory


logger = get_logger("workspace")


class BaseRequest(BaseModel):
    workspace_id: str = Field(
        ..., description="workspace-id to get the running workspace-manager"
    )


class BaseResponse(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    output: t.Any = Field(..., description="output of the command")
    return_code: int = Field(
        ..., description="Any output or errors that occurred during the file edit."
    )


class BaseAction(Action[BaseRequest, BaseResponse], ABC):
    """
    Base class for all actions
    """
    _runs_on_workspace = True
    _display_name = ""
    _tags = ["workspace"]
    _tool_name = "cmdmanagertool"
    workspace: t.Optional[Workspace] = None

    def __init__(self):
        super().__init__()
        self.workspace_id = ""
        self.command = ""
        self.return_code = None

    def set_workspace(self, workspace_factory: WorkspaceFactory):
        self.workspace = workspace_factory.get_registered_manager(self.workspace_id)

    def _setup(self, args: BaseRequest):
        self.workspace_id = args.workspace_id
        if self.workspace is None:
            logger.error("workspace_factory is not set")
            raise ValueError("workspace_factory is not set")

    @abstractmethod
    def execute(
        self, request_data: BaseRequest, authorisation_data: dict
    ) -> BaseResponse:
        pass
