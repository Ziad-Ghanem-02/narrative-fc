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


def _is_number(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, str):
        try:
            float(value)
            return True
        except ValueError:
            return False
    return False


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _numeric_columns(columns: list[str], rows: list[dict[str, Any]]) -> list[str]:
    """Return columns whose non-null values are all numeric."""
    numeric = []
    for column in columns:
        values = [row.get(column) for row in rows if row.get(column) is not None]
        if values and all(_is_number(value) for value in values):
            numeric.append(column)
    return numeric


def _label(column: str) -> str:
    return column.replace("_", " ").title()


def _default_spec(result: dict[str, Any], index: int) -> dict[str, Any]:
    columns = result["columns"]
    data = result["data"]
    chart_type = _default_chart_type(result)
    numeric_columns = _numeric_columns(columns, data)
    categorical_columns = [column for column in columns if column not in numeric_columns]
    palette = CHART_PALETTES[index % len(CHART_PALETTES)]

    if chart_type == "radar":
        return _radar_spec(result, index, categorical_columns, numeric_columns)

    if chart_type == "scatter" and len(numeric_columns) >= 2:
        x_key, y_key = numeric_columns[0], numeric_columns[1]
        return {
            "id": chart_id(result["purpose"], index),
            "type": "scatter",
            "title": result["purpose"],
            "description": "",
            "x_axis": {"data_key": x_key, "label": _label(x_key)},
            "y_axis": {"label": _label(y_key), "format": "number"},
            "series": [
                {
                    "data_key": y_key,
                    "label": _label(y_key),
                    "color": palette[0],
                    "render_as": "line",
                }
            ],
            "data": data,
        }

    if chart_type == "pie" and categorical_columns and numeric_columns:
        x_key, y_key = categorical_columns[0], numeric_columns[0]
        return {
            "id": chart_id(result["purpose"], index),
            "type": "pie",
            "title": result["purpose"],
            "description": "",
            "x_axis": {"data_key": x_key, "label": _label(x_key)},
            "y_axis": {"label": _label(y_key), "format": "number"},
            "series": [
                {
                    "data_key": y_key,
                    "label": _label(y_key),
                    "color": palette[0],
                    "render_as": "bar",
                }
            ],
            "data": data,
        }

    x_key = columns[0] if columns else ""
    if chart_type == "table":
        series_columns = columns[1:] or columns[:1]
    else:
        plottable_columns = [column for column in numeric_columns if column != x_key]
        series_columns = plottable_columns or columns[1:] or columns[:1]
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
        "x_axis": {"data_key": x_key, "label": _label(x_key)},
        "y_axis": {
            "label": "Value",
            "format": "number",
        },
        "series": [
            {
                "data_key": column,
                "label": _label(column),
                "color": palette[position % len(palette)],
                "render_as": render_as,
            }
            for position, column in enumerate(series_columns)
        ],
        "data": data,
    }


def _default_chart_type(result: dict[str, Any]) -> str:
    purpose = result["purpose"].lower()
    columns = result["columns"]
    data = result.get("data", [])
    row_count = len(data)

    if not columns or len(columns) == 1:
        return "table"

    numeric_columns = _numeric_columns(columns, data)
    categorical_columns = [column for column in columns if column not in numeric_columns]
    has_time_axis = columns[0] in {"year", "date"}
    plottable_columns = [column for column in numeric_columns if column != columns[0]]

    if (
        not has_time_axis
        and len(categorical_columns) == 1
        and len(numeric_columns) >= 3
        and 2 <= row_count <= 8
    ):
        return "radar"
    if (
        not has_time_axis
        and len(categorical_columns) == 1
        and len(numeric_columns) == 2
    ):
        return "scatter"
    if (
        not has_time_axis
        and len(categorical_columns) == 1
        and len(numeric_columns) == 1
        and 2 <= row_count <= 7
    ):
        return "pie"
    if not plottable_columns:
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
    if has_time_axis:
        return "line"
    return "bar"


def _normalize_series(values: list[float | None]) -> list[float | None]:
    """Scale a metric's values to a shared 0-100 range so several metrics with
    very different units (e.g. goals vs. goal difference) can share one radar
    axis and remain visually comparable."""
    finite = [value for value in values if value is not None]
    if not finite:
        return [None for _ in values]
    lowest, highest = min(finite), max(finite)
    if highest == lowest:
        return [100.0 if value is not None else None for value in values]
    return [
        None if value is None else round((value - lowest) / (highest - lowest) * 100, 1)
        for value in values
    ]


def _pivot_for_radar(
    rows: list[dict[str, Any]],
    entity_key: str,
    metric_keys: list[str],
    palette: tuple[str, ...],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Recharts' RadarChart needs one row per metric (spoke) and one column
    per entity, which is the transpose of the tabular SQL result (one row per
    team). Pivot the data and normalize each metric so every team's profile
    can be compared on a single radar."""
    entities = []
    seen_slugs: set[str] = set()
    for row in rows:
        raw_name = str(row.get(entity_key, "")).strip() or "Unknown"
        base_slug = re.sub(r"[^0-9a-zA-Z]+", "_", raw_name).strip("_").lower() or "entity"
        slug = base_slug
        suffix = 1
        while slug in seen_slugs:
            suffix += 1
            slug = f"{base_slug}_{suffix}"
        seen_slugs.add(slug)
        entities.append((slug, raw_name, row))

    pivoted = []
    for metric in metric_keys:
        raw_values = [_as_float(row.get(metric)) for _, _, row in entities]
        normalized_values = _normalize_series(raw_values)
        entry: dict[str, Any] = {"metric": _label(metric)}
        for (slug, _, _), value in zip(entities, normalized_values):
            entry[slug] = value
        pivoted.append(entry)

    series = [
        {
            "data_key": slug,
            "label": raw_name,
            "color": palette[position % len(palette)],
            "render_as": "line",
        }
        for position, (slug, raw_name, _) in enumerate(entities)
    ]
    return pivoted, series


def _radar_spec(
    result: dict[str, Any],
    index: int,
    categorical_columns: list[str],
    numeric_columns: list[str],
) -> dict[str, Any]:
    columns = result["columns"]
    data = result["data"]
    entity_key = categorical_columns[0] if categorical_columns else columns[0]
    metric_keys = numeric_columns or [column for column in columns if column != entity_key]
    palette = CHART_PALETTES[index % len(CHART_PALETTES)]
    pivoted, series = _pivot_for_radar(data, entity_key, metric_keys, palette)

    return {
        "id": chart_id(result["purpose"], index),
        "type": "radar",
        "title": result["purpose"],
        "description": "Each metric is scaled 0-100 across the compared teams so it can share one radar chart.",
        "x_axis": {"data_key": "metric", "label": "Metric"},
        "y_axis": {"label": "Relative score (0-100)", "format": "number"},
        "series": series,
        "data": pivoted,
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


def _finalize_radar_spec(spec: dict[str, Any], result: dict[str, Any], index: int) -> dict[str, Any]:
    """Recharts radar charts need one row per metric with one column per
    entity. Neither the LLM nor the naive default builder can be trusted to
    produce that shape, so always rebuild radar data from the raw SQL result."""
    columns = result["columns"]
    data = result["data"]
    numeric_columns = _numeric_columns(columns, data)
    categorical_columns = [column for column in columns if column not in numeric_columns]

    if not numeric_columns or not data:
        return _default_spec(result, index)

    return _radar_spec(result, index, categorical_columns, numeric_columns)


def build_chart_specs(
    results: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    specs = []
    for index, result in enumerate(results):
        try:
            candidate = candidates[index]
            spec = validate_chart_spec(candidate, result, index)
        except (IndexError, TypeError, ValueError):
            spec = _default_spec(result, index)

        if spec["type"] == "radar":
            spec = _finalize_radar_spec(spec, result, index)

        specs.append(spec)
    return specs
