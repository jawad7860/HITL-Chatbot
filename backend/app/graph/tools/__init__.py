from app.graph.tools.github_tool import github_repo_lookup
from app.graph.tools.linkedin_tool import linkedin_profile_lookup

ALL_TOOLS = [github_repo_lookup, linkedin_profile_lookup]

# Names used to detect tool calls and label them in the UI
TOOL_DISPLAY_NAMES = {
    "github_repo_lookup": "GitHub Repo Lookup",
    "linkedin_profile_lookup": "LinkedIn Profile Lookup",
}

__all__ = [
    "ALL_TOOLS",
    "TOOL_DISPLAY_NAMES",
    "github_repo_lookup",
    "linkedin_profile_lookup",
]
