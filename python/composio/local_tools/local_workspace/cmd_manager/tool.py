from typing import Optional

from composio.core.local import Tool
from composio.local_tools.local_workspace.cmd_manager.actions import (
    # CreateFileCmd,
    # EditFile,
    # FindFileCmd,
    # GetCurrentDirCmd,
    # GetPatchCmd,
    # GitRepoTree,
    # GithubCloneCmd,
    # GoToLineNumInOpenFile,
    # OpenFile,
    RunCommandOnWorkspace,
    # Scroll,
    # SearchDirCmd,
    # SearchFileCmd,
)
from composio.workspace.history_processor import (
    HistoryProcessor,
)


class CmdManagerTool(Tool):
    """
    command manager tool for workspace
    """
    history_processor: Optional[HistoryProcessor] = None

    def actions(self) -> list:
        return [
            # FindFileCmd,
            # CreateFileCmd,
            # GoToLineNumInOpenFile,
            # OpenFile,
            # Scroll,
            # SearchFileCmd,
            # SearchDirCmd,
            # EditFile,
            # RunCommandOnWorkspace,
            # GetCurrentDirCmd,
            # GithubCloneCmd,
            # GitRepoTree,
            # GetPatchCmd,
        ]

    def triggers(self) -> list:
        return []

    def set_history_processor(self, history_processor: HistoryProcessor):
        self.history_processor = history_processor

    def get_history_processor(self) -> Optional[HistoryProcessor]:
        return self.history_processor
