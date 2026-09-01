import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "profile.json"


def load_profile():
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        profile = json.load(handle)
    env_user = os.environ.get("GH_PROFILE_USER")
    if env_user:
        profile["username"] = env_user
    return profile


def esc(value):
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))
