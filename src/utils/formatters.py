"""Response formatting helpers."""

from __future__ import annotations

import json
from typing import Any

from src.utils.errors import ToolError


def format_tool_result(data: Any, tool_name: str | None = None) -> str:
    """Format a successful tool result as structured JSON text."""
    result = {"status": "success", "data": data}
    if tool_name:
        result["tool"] = tool_name
    return json.dumps(result, default=str, indent=2)


def format_error_result(error: ToolError) -> str:
    """Format a ToolError as structured JSON text."""
    result = {
        "status": "error",
        "error": {
            "code": error.code,
            "message": error.message,
        },
    }
    if error.details:
        result["error"]["details"] = error.details
    return json.dumps(result, default=str, indent=2)
