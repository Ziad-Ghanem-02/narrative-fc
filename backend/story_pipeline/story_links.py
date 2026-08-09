import re


_CHART_MARKER = re.compile(
    r"(?P<space>\s*)\[(?:chart:(?P<canonical>[a-z0-9-]+)|(?P<legacy>chart-[a-z0-9-]+))\]"
)


def retain_valid_chart_markers(story: str, charts: list[dict]) -> str:
    """Canonicalize valid chart references and remove unmatched chart markers."""
    chart_ids = {
        chart["id"]
        for chart in charts
        if isinstance(chart, dict) and isinstance(chart.get("id"), str)
    }

    def replace(match: re.Match) -> str:
        chart_id = match.group("canonical") or match.group("legacy")
        if chart_id in chart_ids:
            return f"{match.group('space')}[chart:{chart_id}]"
        return ""

    return _CHART_MARKER.sub(replace, story)
