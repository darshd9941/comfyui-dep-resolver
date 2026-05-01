"""Parse ComfyUI workflow JSON and extract node dependencies."""
import json
from pathlib import Path
from typing import Any


def load_workflow(path: str) -> dict:
    """Load a ComfyUI workflow JSON file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Workflow not found: {path}")
    data = json.loads(p.read_text(encoding="utf-8"))
    return data


def extract_class_types(workflow: dict) -> dict[str, list[str]]:
    """
    Extract all class_type references from a workflow.
    Returns {class_type: [node_ids]} mapping.
    """
    class_types: dict[str, list[str]] = {}

    # Handle both API format (dict of node_id → node) and UI format (list of nodes)
    nodes = _extract_nodes(workflow)

    for node_id, node in nodes.items():
        ct = node.get("class_type", "")
        if ct:
            class_types.setdefault(ct, []).append(str(node_id))

    return class_types


def _extract_nodes(workflow: dict) -> dict:
    """Extract nodes from either API or UI workflow format."""
    # API format: top-level dict with node IDs as keys
    if isinstance(workflow, dict):
        first_key = next(iter(workflow), None)
        if first_key is not None:
            first_val = workflow[first_key]
            if isinstance(first_val, dict) and "class_type" in first_val:
                return workflow
        # UI format: dict with "nodes" key
        if "nodes" in workflow:
            return {n["id"]: n for n in workflow["nodes"] if isinstance(n, dict)}

    # List format (some export tools)
    if isinstance(workflow, list):
        return {n.get("id", i): n for i, n in enumerate(workflow) if isinstance(n, dict)}

    return {}


def get_node_connections(workflow: dict) -> dict[str, list[str]]:
    """
    Find which nodes depend on which other nodes via links.
    Returns {node_id: [dependent_node_ids]}.
    """
    nodes = _extract_nodes(workflow)
    connections: dict[str, list[str]] = {}

    for node_id, node in nodes.items():
        inputs = node.get("inputs", {})
        for inp_name, inp_val in inputs.items():
            if isinstance(inp_val, list) and len(inp_val) >= 2:
                # Link format: [source_node_id, output_index]
                source_id = str(inp_val[0])
                connections.setdefault(source_id, []).append(str(node_id))

    return connections


def get_node_info(workflow: dict) -> list[dict[str, Any]]:
    """Get readable info for each node in the workflow."""
    nodes = _extract_nodes(workflow)
    result = []
    for node_id, node in nodes.items():
        result.append({
            "id": str(node_id),
            "class_type": node.get("class_type", "unknown"),
            "title": node.get("title", node.get("_meta", {}).get("title", "")),
            "inputs": list(node.get("inputs", {}).keys()),
            "widget_values": {
                k: v for k, v in node.get("widgets_values", {}).items()
            } if isinstance(node.get("widgets_values"), dict) else [],
        })
    return result


def count_nodes(workflow: dict) -> dict[str, int]:
    """Count total nodes and breakdown by class_type."""
    class_types = extract_class_types(workflow)
    return {
        "total": sum(len(ids) for ids in class_types.values()),
        "unique": len(class_types),
        "by_type": {ct: len(ids) for ct, ids in class_types.items()},
    }
