import json
import re
from typing import Any


ALLOWED_CHART_TYPES = {
    "area",
    "bar",
    "composed",
    "horizontal_bar",
    "line",
    "pie",
    "radar",
    "scatter",
    "stacked_bar",
    "table",
}
SERIES_RENDER_MODES = {"area", "bar", "line"}
CHART_PALETTES = (
    ("#EAB308", "#14B8A6", "#F97316", "#8B5CF6", "#F43F5E"),
    ("#38BDF8", "#A3E635", "#FB7185", "#C084FC", "#FBBF24"),
)


def chart_id(purpose: str, index: int) -> str:
    return f"chart-{index + 1}"


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
    chart_type = _default_chart_type(result)
    render_as = "area" if chart_type == "area" else "bar" if chart_type in {
        "bar",
        "horizontal_bar",
        "stacked_bar",
    } else "line"
    return {
        "id": chart_id(result["purpose"], index),
        "type": chart_type,
        "title": result["purpose"],
        "description": "",
        "x_axis": {"data_key": x_key, "label": x_key.replace("_", " ").title()},
        "y_axis": {
            "label": "Value",
            "format": "number",
        },
        "series": [
            {
                "data_key": column,
                "label": column.replace("_", " ").title(),
                "color": CHART_PALETTES[index % len(CHART_PALETTES)][
                    position % len(CHART_PALETTES[index % len(CHART_PALETTES)])
                ],
                "render_as": render_as,
            }
            for position, column in enumerate(series_columns)
        ],
        "data": result["data"],
    }


def _default_chart_type(result: dict[str, Any]) -> str:
    purpose = result["purpose"].lower()
    columns = result["columns"]
    has_time_axis = bool(columns) and columns[0] in {"year", "date"}

    if not columns or len(columns) == 1:
        return "table"
    if "upset" in purpose or "ranking" in purpose:
        return "horizontal_bar"
    if "representation" in purpose and len(columns) > 2:
        return "stacked_bar"
    if has_time_axis and any(
        term in purpose
        for term in ("diversity", "percentage", "progression", "rate", "trend")
    ):
        return "area"
    return "line"


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
    y_axis = candidate.get("y_axis")
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
    if not isinstance(y_axis, dict) or not isinstance(y_axis.get("label"), str):
        raise ValueError("Chart y-axis label is required.")
    if y_axis.get("format", "number") not in {"number", "percentage"}:
        raise ValueError("Chart y-axis format is unsupported.")
    if not isinstance(series, list) or not series:
        raise ValueError("Chart series are required.")

    validated_series = []
    for position, item in enumerate(series):
        if not isinstance(item, dict) or item.get("data_key") not in columns:
            raise ValueError("Each chart series must use a result column.")
        if not isinstance(item.get("label"), str) or not item["label"].strip():
            raise ValueError("Each chart series needs a label.")
        render_as = item.get(
            "render_as",
            "line" if chart_type in {"area", "line"} else "bar",
        )
        if render_as not in SERIES_RENDER_MODES:
            raise ValueError("Chart series render mode is unsupported.")
        palette = CHART_PALETTES[index % len(CHART_PALETTES)]
        validated_series.append(
            {
                "data_key": item["data_key"],
                "label": item["label"].strip(),
                "color": palette[position % len(palette)],
                "render_as": render_as,
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
        "y_axis": {
            "label": y_axis["label"].strip(),
            "format": y_axis.get("format", "number"),
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
