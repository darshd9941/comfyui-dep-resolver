"""Resolve and install missing ComfyUI custom node dependencies."""
import subprocess
import sys
from pathlib import Path
from typing import Optional
from .registry import load_registry, register_node
from .parser import load_workflow, extract_class_types


def resolve_dependencies(
    workflow_path: str,
    comfyui_dir: Optional[str] = None,
) -> dict:
    """
    Analyze a workflow and report which nodes are available vs missing.
    """
    workflow = load_workflow(workflow_path)
    class_types = extract_class_types(workflow)
    registry = load_registry()

    available = []
    missing = []
    unknown = []

    for ct, node_ids in class_types.items():
        if ct in registry:
            entry = registry[ct]
            if entry.get("builtin"):
                available.append({
                    "class_type": ct,
                    "node_ids": node_ids,
                    "repo": entry["repo"],
                    "status": "builtin",
                })
            else:
                # Check if installed
                installed = _is_node_installed(ct, entry, comfyui_dir)
                available.append({
                    "class_type": ct,
                    "node_ids": node_ids,
                    "repo": entry["repo"],
                    "status": "installed" if installed else "not_installed",
                })
                if not installed:
                    missing.append({
                        "class_type": ct,
                        "node_ids": node_ids,
                        "repo": entry["repo"],
                        "module": entry.get("module", ""),
                    })
        else:
            unknown.append({
                "class_type": ct,
                "node_ids": node_ids,
            })

    return {
        "workflow": workflow_path,
        "total_nodes": sum(len(ids) for ids in class_types.values()),
        "unique_class_types": len(class_types),
        "available": available,
        "missing": missing,
        "unknown": unknown,
    }


def install_missing(
    workflow_path: str,
    comfyui_dir: str = ".",
    dry_run: bool = False,
) -> dict:
    """Install all missing dependencies for a workflow."""
    result = resolve_dependencies(workflow_path, comfyui_dir)
    custom_nodes_dir = Path(comfyui_dir) / "custom_nodes"
    custom_nodes_dir.mkdir(parents=True, exist_ok=True)

    installed = []
    failed = []

    for dep in result["missing"]:
        repo = dep["repo"]
        module = dep.get("module", "")
        repo_name = repo.split("/")[-1]
        target_dir = custom_nodes_dir / repo_name

        if target_dir.exists():
            installed.append({"repo": repo, "status": "already_exists", "path": str(target_dir)})
            continue

        if dry_run:
            installed.append({"repo": repo, "status": "would_install", "path": str(target_dir)})
            continue

        try:
            url = f"https://github.com/{repo}.git"
            subprocess.run(
                ["git", "clone", "--depth", "1", url, str(target_dir)],
                check=True,
                capture_output=True,
                timeout=120,
            )

            # Try pip install requirements
            req_file = target_dir / "requirements.txt"
            if req_file.exists():
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", str(req_file)],
                    check=True,
                    capture_output=True,
                    timeout=300,
                )

            installed.append({"repo": repo, "status": "installed", "path": str(target_dir)})
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            failed.append({"repo": repo, "error": str(e)})

    result["install_results"] = installed
    result["install_failures"] = failed
    return result


def generate_lockfile(workflow_path: str, comfyui_dir: str = ".") -> dict:
    """Generate a lockfile for reproducible workflow environments."""
    result = resolve_dependencies(workflow_path, comfyui_dir)
    lockfile = {
        "workflow": workflow_path,
        "dependencies": {},
    }

    for dep in result["missing"] + [
        {"class_type": a["class_type"], "repo": a["repo"], "module": ""}
        for a in result["available"] if a["status"] != "builtin"
    ]:
        ct = dep["class_type"]
        repo = dep["repo"]
        commit_hash = _get_commit_hash(repo, comfyui_dir)
        lockfile["dependencies"][ct] = {
            "repo": repo,
            "commit": commit_hash,
            "module": dep.get("module", ""),
        }

    return lockfile


def register_custom_node(class_type: str, repo: str, module: str = ""):
    """Register a new custom node in the community registry."""
    register_node(class_type, repo, module)


def _is_node_installed(class_type: str, entry: dict, comfyui_dir: Optional[str]) -> bool:
    """Check if a custom node is installed."""
    if not comfyui_dir:
        return False
    repo_name = entry["repo"].split("/")[-1]
    custom_nodes = Path(comfyui_dir) / "custom_nodes" / repo_name
    return custom_nodes.exists()


def _get_commit_hash(repo: str, comfyui_dir: str) -> Optional[str]:
    """Get the current commit hash of an installed custom node."""
    repo_name = repo.split("/")[-1]
    node_dir = Path(comfyui_dir) / "custom_nodes" / repo_name
    if not node_dir.exists():
        return None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(node_dir),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None
