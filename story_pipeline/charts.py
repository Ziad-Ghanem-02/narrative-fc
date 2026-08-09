import json
import re
from typing import Any


ALLOWED_CHART_TYPES = {"line", "bar", "stacked_bar", "scatter", "table"}
CHART_COLORS = ["#2563eb", "#f97316", "#16a34a", "#9333ea", "#dc2626"]


def chart_id(purpose: str, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", purpose.lower()).strip("-")
    return f"chart-{index + 1}-{slug or 'data'}"


def parse_chart_specs(response: str) -> list[dict[str, Any]]:
    content = response.strip()
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content).strip()

    parsed = json.loads(content)
    if not isinstance(parsed, list):
        raise ValueError("Chart specifications must be a JSON array.")
    return parsed


def _default_spec(result: dict[str, Any], index: int) -> dict[str, Any]:
    columns = result["columns"]
    x_key = columns[0] if columns else ""
    series_columns = columns[1:] or columns[:1]
    return {
        "id": chart_id(result["purpose"], index),
        "type": "line" if len(columns) > 1 else "table",
        "title": result["purpose"],
        "description": "",
        "x_axis": {"data_key": x_key, "label": x_key.replace("_", " ").title()},
        "series": [
            {
                "data_key": column,
                "label": column.replace("_", " ").title(),
                "color": CHART_COLORS[position % len(CHART_COLORS)],
            }
            for position, column in enumerate(series_columns)
        ],
        "data": result["data"],
    }


def validate_chart_spec(
    candidate: dict[str, Any],
    result: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    if not isinstance(candidate, dict):
        raise ValueError("Each chart specification must be an object.")

    columns = result["columns"]
    chart_type = candidate.get("type")
    title = candidate.get("title")
    description = candidate.get("description", "")
    x_axis = candidate.get("x_axis")
    series = candidate.get("series")

    if chart_type not in ALLOWED_CHART_TYPES:
        raise ValueError("Unsupported chart type.")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Chart title is required.")
    if not isinstance(description, str):
        raise ValueError("Chart description must be text.")
    if not isinstance(x_axis, dict) or x_axis.get("data_key") not in columns:
        raise ValueError("Chart x-axis must use a result column.")
    if not isinstance(x_axis.get("label"), str) or not x_axis["label"].strip():
        raise ValueError("Chart x-axis label is required.")
    if not isinstance(series, list) or not series:
        raise ValueError("Chart series are required.")

    validated_series = []
    for position, item in enumerate(series):
        if not isinstance(item, dict) or item.get("data_key") not in columns:
            raise ValueError("Each chart series must use a result column.")
        if not isinstance(item.get("label"), str) or not item["label"].strip():
            raise ValueError("Each chart series needs a label.")
        color = item.get("color")
        if color not in CHART_COLORS:
            color = CHART_COLORS[position % len(CHART_COLORS)]
        validated_series.append(
            {
                "data_key": item["data_key"],
                "label": item["label"].strip(),
                "color": color,
            }
        )

    return {
        "id": chart_id(result["purpose"], index),
        "type": chart_type,
        "title": title.strip(),
        "description": description.strip(),
        "x_axis": {
            "data_key": x_axis["data_key"],
            "label": x_axis["label"].strip(),
        },
        "series": validated_series,
        "data": result["data"],
    }


def build_chart_specs(
    results: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    specs = []
    for index, result in enumerate(results):
        try:
            candidate = candidates[index]
            specs.append(validate_chart_spec(candidate, result, index))
        except (IndexError, TypeError, ValueError):
            specs.append(_default_spec(result, index))
    return specs
