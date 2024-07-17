from pathlib import Path
from typing import List, Optional, Type

from pydantic import BaseModel, Field

from composio.tools.local.base import Action
from composio.tools.local.base.utils.grep_utils import get_files_excluding_gitignore
from composio.tools.local.base.utils.repomap import RepoMap


class GetRepoMapRequest(BaseModel):
    code_directory: str = Field(
        ...,
        description="Absolute path to the root directory of the repository or codebase.",
        examples=[
            "/home/user/projects/my-repo",
            "/Users/username/Documents/my-project",
            "/project",
        ],
    )
    files_of_interest: List[str] = Field(
        default=[],
        description="List of file paths (relative to repository root) that are of particular interest for generating the repo map",
        examples=[
            ["src/main.py", "tests/test_main.py", "README.md"],
            ["main.py", "test_main.py", "README.md"],
        ],
    )
    primary_file_paths: List[str] = Field(
        default=[],
        description="List of file paths (relative to repository root) that around which the repo map should be generated. Primary file won't be included in the repo map.",
    )
    mentioned_idents: List[str] = Field(
        default=[],
        description="List of identifiers (e.g. function names, class names) that the focus of the repo map should be on",
    )


class GetRepoMapResponse(BaseModel):
    repository_map: Optional[str] = Field(
        default=None,
        description="Generated repository map as a string, containing a structured view of important code elements",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Detailed error message if an error occurred during map generation",
    )


class GetRepoMap(Action[GetRepoMapRequest, GetRepoMapResponse]):
    """
    Generates a comprehensive repository map for specified files of interest within a given repository.

    This action analyzes the repository structure, focusing on the files specified as 'files_of_interest'.
    It provides a structured view of important code elements, helping software agents understand
    the layout and key components of the codebase.
    """

    _display_name = "Generate Repository Map"
    _request_schema: Type[GetRepoMapRequest] = GetRepoMapRequest
    _response_schema: Type[GetRepoMapResponse] = GetRepoMapResponse
    _tags = ["repository", "code-structure", "analysis"]
    _tool_name = "codemap"

    def execute(
        self, request_data: GetRepoMapRequest, authorisation_data: dict = {}
    ) -> dict:
        repo_root = Path(request_data.code_directory).resolve()

        if not repo_root.exists():
            return {
                "error_message": f"Repository root path '{repo_root}' does not exist or is inaccessible."
            }

        try:
            # Retrieve all files in the repository, excluding those specified in .gitignore
            all_repository_files = get_files_excluding_gitignore(repo_root)

            # Convert absolute paths to paths relative to the repository root, considering only .py files
            relative_file_paths = [
                str(Path(file).relative_to(repo_root))
                for file in all_repository_files
                if file.endswith(".py")
            ]

            # Generate the repository map
            repo_map_generator = RepoMap(root=repo_root)
            generated_map = repo_map_generator.get_repo_map(
                chat_files=set(request_data.primary_file_paths),
                other_files=relative_file_paths,
                mentioned_fnames=set(request_data.files_of_interest),
                mentioned_idents=set(request_data.mentioned_idents),
            )

            return {
                "status": "success",
                "repository_map": generated_map,
                "error_message": None,
            }

        except Exception as e:
            return {
                "repository_map": None,
                "error_message": f"An error occurred while generating the repository map: {str(e)}. Please ensure all paths are correct and you have necessary permissions.",
            }
