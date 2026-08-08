from typing import Any, TypedDict



class WorldCupState(TypedDict):

    question: str

    queries: list[dict[str, str]]

    results: list[dict[str, Any]]

    evidence: str

    plan: str

    story: str

    charts: list[dict[str, Any]]