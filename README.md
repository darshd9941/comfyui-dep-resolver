# comfyui-dep-resolver

# ðŸ”§ ComfyUI Workflow Dependency Resolver

> `npm install` for ComfyUI workflows â€” parse workflow JSON, find missing custom nodes, and auto-install them.

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
| `validate` | Quick check â€” exit 0 if valid, exit 1 if missing deps |
| `register` | Add a custom node to the community registry |

## Usage Examples

### Analyze a workflow
```bash
$ comfyui-dep-resolver resolve my-workflow.json

â•­â”€â”€â”€â”€â”€â”€ Dependency Report â”€â”€â”€â”€â”€â”€â•®
â”‚ Workflow: my-workflow.json     â”‚
â”‚ Total nodes: 24                â”‚
â”‚ Unique class types: 12         â”‚
â”‚ Available: 9                   â”‚
â”‚ Missing: 2                     â”‚
â”‚ Unknown: 1                     â”‚
â•°â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â•¯

Missing Dependencies
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ Class Type           â”‚ Node IDs  â”‚ Repository                   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ FaceDetailer         â”‚ 15, 18    â”‚ ltdrdata/ComfyUI-Impact-Pack â”‚
â”‚ IPAdapterApply       â”‚ 20        â”‚ cubiq/ComfyUI_IPAdapter_plus â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Install missing nodes
```bash
$ comfyui-dep-resolver install my-workflow.json -d ./ComfyUI
Installing 2 missing dependencies...
  âœ“ Installed ltdrdata/ComfyUI-Impact-Pack
  âœ“ Installed cubiq/ComfyUI_IPAdapter_plus
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

1. **Parse** â€” Reads workflow JSON (API or UI format), extracts all `class_type` references
2. **Lookup** â€” Checks each class_type against the built-in + user registry
3. **Resolve** â€” Reports which are builtin, installed, missing, or unknown
4. **Install** â€” Clones missing repos into `custom_nodes/` and pip-installs requirements
5. **Lock** â€” Captures commit hashes for reproducible environments

## Contributing

Contributions welcome! Especially:
- New registry entries for custom nodes
- Support for non-git installation methods (pip, direct download)
- Workflow format parsers for other tools

## License

MIT License â€” see [LICENSE](LICENSE) for details.


## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Clone the Repository

```bash
git clone https://github.com/darshd9941/comfyui-dep-resolver.git
cd comfyui-dep-resolver
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit .env and add your API keys:
   ```bash
   # Required for Claude vision features
   ANTHROPIC_API_KEY=your-api-key-here
   ```

## Usage

### Web App (if applicable)

```bash
streamlit run app.py
```

### CLI Usage

```bash
python main.py --help
```

### Python API

```python
from module import MainClass

# Initialize the tool
tool = MainClass()

# Use the tool
result = tool.process("input")
print(result)
```

## Configuration

- .env - Environment variables (API keys, settings)
- config.yaml - Configuration file (if applicable)

## Examples

See the examples/ directory for detailed usage examples.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See LICENSE file for details.
