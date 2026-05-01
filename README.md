# 🔧 ComfyUI Workflow Dependency Resolver

> `npm install` for ComfyUI workflows — parse workflow JSON, find missing custom nodes, and auto-install them.

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Nodes-orange)

## The Problem

You download a ComfyUI workflow JSON from Civitai, a Discord server, or a GitHub repo. You load it in ComfyUI and... half the nodes are red. Missing custom nodes. You spend 30 minutes Googling each class_type, finding the right GitHub repo, cloning it, installing requirements, restarting ComfyUI. Repeat for every new workflow.

## The Solution

```bash
# Analyze what's missing
comfyui-dep-resolver resolve workflow.json --comfyui-dir ./ComfyUI

# Install everything automatically
comfyui-dep-resolver install workflow.json --comfyui-dir ./ComfyUI

# Generate a lockfile for reproducibility
comfyui-dep-resolver lock workflow.json -o workflow.lock.json
```

## Quick Start

```bash
# Install
git clone https://github.com/darshd9941/comfyui-dep-resolver.git
cd comfyui-dep-resolver
pip install -e .

# Or install from PyPI (when published)
pip install comfyui-dep-resolver
```

## Commands

| Command | Description |
|---------|-------------|
| `resolve` | Analyze workflow, report available/missing/unknown nodes |
| `install` | Auto-install missing custom nodes via git clone |
| `lock` | Generate a lockfile with commit hashes for reproducibility |
| `info` | Show detailed node breakdown for a workflow |
| `validate` | Quick check — exit 0 if valid, exit 1 if missing deps |
| `register` | Add a custom node to the community registry |

## Usage Examples

### Analyze a workflow
```bash
$ comfyui-dep-resolver resolve my-workflow.json

╭────── Dependency Report ──────╮
│ Workflow: my-workflow.json     │
│ Total nodes: 24                │
│ Unique class types: 12         │
│ Available: 9                   │
│ Missing: 2                     │
│ Unknown: 1                     │
╰───────────────────────────────╯

Missing Dependencies
┌──────────────────────┬───────────┬──────────────────────────────┐
│ Class Type           │ Node IDs  │ Repository                   │
├──────────────────────┼───────────┼──────────────────────────────┤
│ FaceDetailer         │ 15, 18    │ ltdrdata/ComfyUI-Impact-Pack │
│ IPAdapterApply       │ 20        │ cubiq/ComfyUI_IPAdapter_plus │
└──────────────────────┴───────────┴──────────────────────────────┘
```

### Install missing nodes
```bash
$ comfyui-dep-resolver install my-workflow.json -d ./ComfyUI
Installing 2 missing dependencies...
  ✓ Installed ltdrdata/ComfyUI-Impact-Pack
  ✓ Installed cubiq/ComfyUI_IPAdapter_plus
```

### Dry run (see what would be installed)
```bash
$ comfyui-dep-resolver install my-workflow.json --dry-run
```

### Validate for CI/CD
```bash
$ comfyui-dep-resolver validate workflow.json
# Exit code 0 = all deps met, 1 = missing deps
```

## Community Registry

The built-in registry covers 50+ popular custom nodes. You can extend it:

```bash
# Register a new node
comfyui-dep-resolver register "MyCustomNode" "username/repo-name" --module "my_module"
```

Or edit `registry.json` directly and submit a PR.

## Lockfiles

Generate a lockfile to pin exact commit hashes:

```bash
comfyui-dep-resolver lock workflow.json -o workflow.lock.json
```

The lockfile format:
```json
{
  "workflow": "my-workflow.json",
  "dependencies": {
    "FaceDetailer": {
      "repo": "ltdrdata/ComfyUI-Impact-Pack",
      "commit": "abc123...",
      "module": "detailer"
    }
  }
}
```

## Docker Support

```bash
# In a Dockerfile
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN pip install -e .

# Validate workflow in build
RUN comfyui-dep-resolver validate /workflows/my-workflow.json
```

## How It Works

1. **Parse** — Reads workflow JSON (API or UI format), extracts all `class_type` references
2. **Lookup** — Checks each class_type against the built-in + user registry
3. **Resolve** — Reports which are builtin, installed, missing, or unknown
4. **Install** — Clones missing repos into `custom_nodes/` and pip-installs requirements
5. **Lock** — Captures commit hashes for reproducible environments

## Contributing

Contributions welcome! Especially:
- New registry entries for custom nodes
- Support for non-git installation methods (pip, direct download)
- Workflow format parsers for other tools

## License

MIT License — see [LICENSE](LICENSE) for details.
