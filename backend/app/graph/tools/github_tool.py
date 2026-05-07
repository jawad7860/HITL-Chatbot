"""GitHub repository lookup tool."""
import logging
from typing import Any, Dict, List
from urllib.parse import urlparse
import httpx
from langchain_core.tools import tool
from app.core.config import get_settings


logger = logging.getLogger(__name__)
GITHUB_API = "https://api.github.com"


def _parse_repo_identifier(identifier: str) -> tuple[str, str]:
    """Accept either 'owner/repo' or a full GitHub URL. Returns (owner, repo)."""
    identifier = identifier.strip().rstrip("/")

    if identifier.startswith(("http://", "https://")):
        path = urlparse(identifier).path.strip("/")
        parts = path.split("/")
        if len(parts) < 2:
            raise ValueError(f"Could not parse GitHub URL: {identifier}")
        return parts[0], parts[1]

    if "/" in identifier:
        owner, repo = identifier.split("/", 1)
        return owner, repo.split("/")[0]

    raise ValueError(
        f"Invalid repo identifier: {identifier!r}. "
        "Expected 'owner/repo' or a github.com URL."
    )


def _headers() -> Dict[str, str]:
    h = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "hitl-chatbot/1.0",
    }
    token = get_settings().github_token
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


@tool
async def github_repo_lookup(repo_identifier: str) -> Dict[str, Any]:
    """Look up metadata about a public GitHub repository.

    Args:
        repo_identifier: Either 'owner/repo' (e.g. 'fastapi/fastapi') or a full
            GitHub URL (e.g. 'https://github.com/fastapi/fastapi').

    Returns repo description, stars, language, top-level files, and recent
    commits.
    """
    try:
        owner, repo = _parse_repo_identifier(repo_identifier)
    except ValueError as e:
        return {"error": str(e)}

    async with httpx.AsyncClient(headers=_headers(), timeout=15.0) as client:
        try:
            # Repo metadata
            r = await client.get(f"{GITHUB_API}/repos/{owner}/{repo}")
            if r.status_code == 404:
                return {"error": f"Repo not found: {owner}/{repo}"}
            r.raise_for_status()
            meta = r.json()

            # Top-level contents
            contents_r = await client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/contents"
            )
            top_files: List[str] = []
            if contents_r.status_code == 200:
                top_files = [
                    item["name"] for item in contents_r.json()[:15]
                ]

            # Last 5 commits
            commits_r = await client.get(
                f"{GITHUB_API}/repos/{owner}/{repo}/commits",
                params={"per_page": 5},
            )
            recent_commits: List[Dict[str, str]] = []
            if commits_r.status_code == 200:
                for c in commits_r.json():
                    recent_commits.append({
                        "sha": c["sha"][:7],
                        "message": c["commit"]["message"].split("\n")[0][:120],
                        "author": (c.get("author") or {}).get("login")
                                  or c["commit"]["author"]["name"],
                        "date": c["commit"]["author"]["date"],
                    })
        except httpx.HTTPError as e:
            logger.exception("GitHub API error")
            return {"error": f"GitHub API error: {e}"}

    return {
        "full_name": meta.get("full_name"),
        "description": meta.get("description") or "(no description)",
        "url": meta.get("html_url"),
        "stars": meta.get("stargazers_count"),
        "forks": meta.get("forks_count"),
        "open_issues": meta.get("open_issues_count"),
        "language": meta.get("language"),
        "license": (meta.get("license") or {}).get("spdx_id"),
        "default_branch": meta.get("default_branch"),
        "created_at": meta.get("created_at"),
        "updated_at": meta.get("updated_at"),
        "top_files": top_files,
        "recent_commits": recent_commits,
    }
