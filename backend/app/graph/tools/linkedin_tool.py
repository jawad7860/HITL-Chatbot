"""Mocked LinkedIn profile lookup tool."""
import asyncio
import hashlib
from typing import Any, Dict
from langchain_core.tools import tool


def _deterministic_mock(profile_url: str) -> Dict[str, Any]:
    """Return a deterministic-but-varied mock based on a hash of the URL.

    Same URL → same response (helps with debugging). Different URLs →
    different shapes so demos don't all look identical.
    """
    seed = int(hashlib.md5(profile_url.encode()).hexdigest()[:8], 16)
    names = ["Aisha Khan", "Daniel Park", "Maria Rossi", "Tomás Silva", "Yuki Tanaka"]
    titles = [
        "Senior ML Engineer",
        "Staff Software Engineer",
        "Director of Engineering",
        "AI Research Lead",
        "Principal Data Scientist",
    ]
    companies = ["Stripe", "Databricks", "Anthropic", "Nvidia", "Hugging Face"]
    locations = ["San Francisco, CA", "London, UK", "Berlin, DE", "Singapore", "Toronto, CA"]
    pick = lambda lst: lst[seed % len(lst)]
    return {
        "url": profile_url,
        "name": pick(names),
        "headline": f"{pick(titles)} at {pick(companies)}",
        "location": pick(locations),
        "current_role": {
            "title": pick(titles),
            "company": pick(companies),
            "duration_years": (seed % 7) + 1,
        },
        "previous_roles": [
            {"title": "Software Engineer", "company": "Google", "years": "2018-2021"},
            {"title": "Software Engineer Intern", "company": "Microsoft", "years": "Summer 2017"},
        ],
        "skills": ["Python", "PyTorch", "Distributed Systems", "LLMs", "Kubernetes"],
        "_meta": {
            "source": "mocked",
            "note": (
                "This is a mocked response. Production would call Proxycurl or "
                "an equivalent paid LinkedIn scraping API."
            ),
        },
    }


@tool
async def linkedin_profile_lookup(profile_url: str) -> Dict[str, Any]:
    """Look up information about a LinkedIn profile.

    Args:
        profile_url: The full URL to a LinkedIn profile, e.g.
            'https://linkedin.com/in/jane-doe'.

    Returns a dict with name, headline, current role, previous roles, and skills.
    """
    # Simulate scraping latency so the async background-task path is observable.
    await asyncio.sleep(2.5)
    return _deterministic_mock(profile_url)
