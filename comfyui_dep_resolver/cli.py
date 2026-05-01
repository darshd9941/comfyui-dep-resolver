"""CLI for resolving and installing ComfyUI workflow dependencies."""
import json
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .resolver import resolve_dependencies, install_missing, generate_lockfile, register_custom_node
from .parser import load_workflow, count_nodes, get_node_info

console = Console()


@click.group()
@click.version_option(package_name="comfyui-dep-resolver")
def cli():
    """ComfyUI Workflow Dependency Resolver — resolve missing nodes, auto-install."""
    pass


@cli.command()
@click.argument("workflow_json")
@click.option("--comfyui-dir", "-d", default=".", help="Path to ComfyUI installation")
def resolve(workflow_json, comfyui_dir):
    """Analyze a workflow and report available/missing/unknown nodes."""
    result = resolve_dependencies(workflow_json, comfyui_dir)

    # Summary panel
    console.print(Panel(
        f"[bold]Workflow:[/] {result['workflow']}\n"
        f"[bold]Total nodes:[/] {result['total_nodes']}\n"
        f"[bold]Unique class types:[/] {result['unique_class_types']}\n"
        f"[green]Available:[/] {len(result['available'])}\n"
        f"[red]Missing:[/] {len(result['missing'])}\n"
        f"[yellow]Unknown:[/] {len(result['unknown'])}",
        title="Dependency Report",
    ))

    if result["missing"]:
        table = Table(title="Missing Dependencies", show_lines=True)
        table.add_column("Class Type", style="red")
        table.add_column("Node IDs")
        table.add_column("Repository", style="cyan")
        for dep in result["missing"]:
            table.add_row(
                dep["class_type"],
                ", ".join(dep["node_ids"]),
                dep["repo"],
            )
        console.print(table)

    if result["unknown"]:
        console.print("\n[yellow]Unknown class types (not in registry):[/]")
        for u in result["unknown"]:
            console.print(f"  • {u['class_type']} (nodes: {', '.join(u['node_ids'])})")

    if not result["missing"] and not result["unknown"]:
        console.print("\n[green]✓ All dependencies resolved![/]")


@cli.command()
@click.argument("workflow_json")
@click.option("--comfyui-dir", "-d", default=".", help="Path to ComfyUI installation")
@click.option("--dry-run", is_flag=True, help="Show what would be installed without installing")
def install(workflow_json, comfyui_dir, dry_run):
    """Install missing custom nodes for a workflow."""
    result = install_missing(workflow_json, comfyui_dir, dry_run=dry_run)

    if not result["missing"]:
        console.print("[green]✓ All dependencies already installed![/]")
        return

    mode = "[yellow]DRY RUN[/]" if dry_run else "[green]Installing[/]"
    console.print(f"\n{mode} {len(result['missing'])} missing dependencies...\n")

    for item in result.get("install_results", []):
        status = item["status"]
        repo = item["repo"]
        if status == "installed":
            console.print(f"  [green]✓[/] Installed {repo}")
        elif status == "already_exists":
            console.print(f"  [dim]•[/] Already exists: {repo}")
        elif status == "would_install":
            console.print(f"  [yellow]→[/] Would install: {repo}")

    for item in result.get("install_failures", []):
        console.print(f"  [red]✗[/] Failed: {item['repo']} — {item['error']}")


@cli.command()
@click.argument("workflow_json")
@click.option("--comfyui-dir", "-d", default=".", help="Path to ComfyUI installation")
@click.option("-o", "--output", default=None, help="Output file (default: stdout)")
def lock(workflow_json, comfyui_dir, output):
    """Generate a lockfile for reproducible workflow environments."""
    lockfile = generate_lockfile(workflow_json, comfyui_dir)
    content = json.dumps(lockfile, indent=2)
    if output:
        Path(output).write_text(content, encoding="utf-8")
        console.print(f"[green]✓ Lockfile written to {output}[/]")
    else:
        console.print(content)


@cli.command()
@click.argument("workflow_json")
def info(workflow_json):
    """Show detailed info about all nodes in a workflow."""
    workflow = load_workflow(workflow_json)
    counts = count_nodes(workflow)
    nodes = get_node_info(workflow)

    console.print(Panel(
        f"[bold]Total nodes:[/] {counts['total']}\n"
        f"[bold]Unique types:[/] {counts['unique']}",
        title="Workflow Info",
    ))

    if counts["by_type"]:
        table = Table(title="Node Breakdown")
        table.add_column("Class Type", style="cyan")
        table.add_column("Count", justify="right")
        for ct, cnt in sorted(counts["by_type"].items(), key=lambda x: -x[1]):
            table.add_row(ct, str(cnt))
        console.print(table)

    table = Table(title="All Nodes", show_lines=True)
    table.add_column("ID", style="dim")
    table.add_column("Type", style="cyan")
    table.add_column("Title")
    table.add_column("Inputs")
    for n in nodes:
        table.add_row(
            n["id"],
            n["class_type"],
            n.get("title", ""),
            ", ".join(n["inputs"][:5]) + ("..." if len(n["inputs"]) > 5 else ""),
        )
    console.print(table)


@cli.command()
@click.argument("class_type")
@click.argument("repo")
@click.option("--module", "-m", default="", help="Python module name")
def register(class_type, repo, module):
    """Register a custom node in the community registry."""
    register_custom_node(class_type, repo, module)
    console.print(f"[green]✓ Registered {class_type} → {repo}[/]")


@cli.command()
@click.argument("workflow_json")
def validate(workflow_json):
    """Quick validate — exit code 0 if all deps met, 1 otherwise."""
    result = resolve_dependencies(workflow_json)
    if result["missing"] or result["unknown"]:
        for dep in result["missing"]:
            console.print(f"[red]MISSING[/] {dep['class_type']} ({dep['repo']})")
        for u in result["unknown"]:
            console.print(f"[yellow]UNKNOWN[/] {u['class_type']}")
        raise SystemExit(1)
    console.print("[green]✓ Workflow is valid — all dependencies available[/]")


if __name__ == "__main__":
    cli()
