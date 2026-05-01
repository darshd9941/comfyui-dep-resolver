"""Community registry mapping ComfyUI node class_types to their source repos."""
import json
from pathlib import Path

REGISTRY_FILE = Path(__file__).parent / "registry.json"

# Built-in registry — extend via PRs or `comfyui-dep-resolver register`
BUILTIN_REGISTRY = {
    "KSampler": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "CheckpointLoaderSimple": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "CLIPTextEncode": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "EmptyLatentImage": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "VAEDecode": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "VAEEncode": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "SaveImage": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "LoadImage": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "ImageBlend": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "PreviewImage": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "LatentUpscale": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "ImageScale": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "ControlNetApply": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    # Popular custom nodes
    "ImageChooser": {"repo": "rgthree/rgthree-comfy", "module": "image_chooser"},
    "RandomBattery": {"repo": "rgthree/rgthree-comfy", "module": "random_battery"},
    "Note": {"repo": "rgthree/rgthree-comfy", "module": "note"},
    "Reroute": {"repo": "cgwebber/comfyui-reroute-nodes", "module": "reroute_node"},
    "PromptSchedule": {"repo": "Kosinkadink/ComfyUI-Advanced-ControlNet", "module": "control_nodes"},
    "LoadDiffusionModel": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "LoraLoader": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "CLIPVisionEncode": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "IPAdapterApply": {"repo": "cubiq/ComfyUI_IPAdapter_plus", "module": "ipadapter_node"},
    "FaceDetailer": {"repo": "ltdrdata/ComfyUI-Impact-Pack", "module": "detailer"},
    "SEGSDetailer": {"repo": "ltdrdata/ComfyUI-Impact-Pack", "module": "detailer"},
    "SEGSLabel": {"repo": "ltdrdata/ComfyUI-Impact-Pack", "module": "detailer"},
    "UltralyticsDetectorProvider": {"repo": "ltdrdata/ComfyUI-Impact-Pack", "module": "ultralytics"},
    "SAMLoader": {"repo": "davemaneuworhs/ComfyUI-Impact-Pack", "module": "sam_loader"},
    "MarkdownNote": {"repo": "tridevcom/ComfyUI_MarkdownNote", "module": "markdown_note"},
    "JWFloatToInteger": {"repo": "jamesWalker55/comfyui-various", "module": "jw_float_to_integer"},
    "JWImageForceResize": {"repo": "jamesWalker55/comfyui-various", "module": "jw_image_force_resize"},
    "ColorMatch": {"repo": "solo9999/ComfyUI_essentials", "module": "color_match"},
    "ImageRemoveBackground": {"repo": "pythongosssss/ComfyUI-Custom-Scripts", "module": "remove_background"},
    "MiDaS-DepthMap": {"repo": "comfyanonymous/ComfyUI", "module": "nodes", "builtin": True},
    "DepthAnythingV2": {"repo": "if-ai/ComfyUI-IF_AI_tools", "module": "depth_anything"},
    "VideoHelperSuite": {"repo": "Kosinkadink/ComfyUI-VideoHelperSuite", "module": "video_nodes"},
    "MMAudio": {"repo": "MMAudio", "module": "mm_audio_nodes"},
    "NovaSR": {"repo": "ssitu/ComfyUI_UltimateSDUpscale", "module": "ultimate_sd_upscale"},
    "WanImageToVideo": {"repo": "kijai/ComfyUI-WanVideoWrapper", "module": "wan_video"},
}


def load_registry() -> dict:
    """Load the combined registry (built-in + user-added)."""
    registry = dict(BUILTIN_REGISTRY)
    if REGISTRY_FILE.exists():
        try:
            user_registry = json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))
            registry.update(user_registry)
        except (json.JSONDecodeError, OSError):
            pass
    return registry


def save_registry(registry: dict):
    """Save user-added entries to the registry file."""
    user_only = {k: v for k, v in registry.items() if k not in BUILTIN_REGISTRY}
    REGISTRY_FILE.write_text(json.dumps(user_only, indent=2), encoding="utf-8")


def register_node(class_type: str, repo: str, module: str = ""):
    """Register a new class_type → repo mapping."""
    registry = load_registry()
    registry[class_type] = {"repo": repo, "module": module}
    save_registry(registry)
