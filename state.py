from typing import TypedDict
from typing import TypedDict, List



class WorldCupState(TypedDict):

    question: str

    queries: list

    results: list

    evidence: list

    plan: str

    story: str

    charts: List