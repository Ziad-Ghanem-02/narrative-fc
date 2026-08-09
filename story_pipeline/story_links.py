import re


_CHART_MARKER = re.compile(r"\s*\[chart:([a-z0-9-]+)\]")


def retain_valid_chart_markers(story: str, charts: list[dict]) -> str:
    """Remove chart markers that do not refer to a returned chart."""
    chart_ids = {chart["id"] for chart in charts}

    def replace(match: re.Match) -> str:
        return match.group(0) if match.group(1) in chart_ids else ""

    return _CHART_MARKER.sub(replace, story)
