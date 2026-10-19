"""Stream Deck button creator.

Generates a worker .bat (ASCII + CRLF + chcp 65001), a launcher .vbs,
and inserts the button into the active Stream Deck Plus manifest.json
at the next free slot (or a user-specified position).

Usage:
    python create-button.py \
        --label "DaVinci" \
        --folder "C:\\projects\\my-app" \
        --color "#fbbf24" \
        --command continue
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from pathlib import Path

PROFILES_ROOT = Path(os.environ["APPDATA"]) / "Elgato" / "StreamDeck" / "ProfilesV3"
SCRIPTS_DIR = Path.home() / "StreamDeckScripts"
SD_PLUS_MODEL = "20GBD9901"


def find_current_page() -> Path:
    """Find the manifest.json of the currently active SD Plus page."""
    for sd_profile in sorted(PROFILES_ROOT.glob("*.sdProfile")):
        top_manifest = sd_profile / "manifest.json"
        if not top_manifest.exists():
            continue
        try:
            data = json.loads(top_manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        device_info = data.get("Device") or {}
        if SD_PLUS_MODEL not in (device_info.get("Model") or ""):
            continue
        pages_block = data.get("Pages") or {}
        current = (pages_block.get("Current") or "").upper()
        if not current:
            continue
        candidate = sd_profile / "Profiles" / current / "manifest.json"
        if candidate.exists():
            return candidate
        candidate_lc = sd_profile / "Profiles" / current.lower() / "manifest.json"
        if candidate_lc.exists():
            return candidate_lc
    raise RuntimeError("Active Stream Deck Plus page not found")


def get_keypad_actions(page_manifest: dict) -> dict:
    for controller in page_manifest.get("Controllers", []):
        if controller.get("Type") == "Keypad":
            return controller.get("Actions") or {}
    raise RuntimeError("No Keypad controller in page manifest")


def find_free_slot(actions: dict) -> str:
    occupied = set(actions.keys())
    for row in range(2):
        for col in range(4):
            slot = f"{col},{row}"
            if slot not in occupied:
                return slot
    raise RuntimeError("Page is full (4x2 = 8 slots all occupied)")


def write_bat_crlf(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = b"\r\n".join(line.encode("ascii") for line in lines) + b"\r\n"
    path.write_bytes(body)


def write_vbs(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def safe_filename(label: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", label.lower()).strip("-")
    return slug or "button"


SKIP_PERMISSIONS_FLAG = " --dangerously-skip-permissions"


def build_worker_bat_lines(
    folder: str,
    command: str,
    prompt: str | None,
    skip_permissions: bool = False,
) -> list[str]:
    """Build the lines of the worker .bat.

    By default Claude Code is started normally, so it asks before it runs
    commands or edits files. Pass skip_permissions=True (opt-in) to add
    --dangerously-skip-permissions, which removes those confirmations.
    """
    flag = SKIP_PERMISSIONS_FLAG if skip_permissions else ""
    n = "nul"
    lines = [
        "@echo off",
        f"chcp 65001 >{n} 2>&1",
        f'cd /d "{folder}"',
    ]
    if command == "continue":
        lines.append(f"claude --continue{flag}")
    elif command == "new":
        lines.append(f"claude{flag}")
    elif command == "resume":
        lines.append(f"claude --resume{flag}")
    elif command == "prompt":
        if not prompt:
            raise ValueError("--prompt is required when --command=prompt")
        prompt_file = SCRIPTS_DIR / "prompts" / f"{safe_filename(prompt[:30])}.txt"
        prompt_file.parent.mkdir(parents=True, exist_ok=True)
        prompt_file.write_text(prompt, encoding="utf-8")
        lines.append(f'set /p PROMPT=<"{prompt_file}"')
        lines.append(f'claude -p "%PROMPT%"{flag}')
        lines.append("pause")
    else:
        raise ValueError(f"Unknown command: {command}")
    return lines


def build_vbs(worker_bat: Path) -> str:
    return f'CreateObject("WScript.Shell").Run "cmd /k {worker_bat}", 1, False\r\n'


def insert_button(
    page_manifest_path: Path,
    position: str,
    title: str,
    color: str,
    vbs_path: Path,
) -> None:
    data = json.loads(page_manifest_path.read_text(encoding="utf-8"))
    actions = get_keypad_actions(data)
    button = {
        "ActionID": str(uuid.uuid4()),
        "LinkedTitle": True,
        "Name": "Open",
        "Plugin": {
            "Name": "Open",
            "UUID": "com.elgato.streamdeck.system.open",
            "Version": "1.0",
        },
        "Resources": None,
        "Settings": {
            "openInBrowser": False,
            "path": str(vbs_path),
        },
        "State": 0,
        "States": [
            {
                "FontFamily": "",
                "FontSize": 12,
                "FontStyle": "",
                "FontUnderline": False,
                "OutlineThickness": 2,
                "ShowTitle": True,
                "Title": title,
                "TitleAlignment": "bottom",
                "TitleColor": color,
            }
        ],
        "UUID": "com.elgato.streamdeck.system.open",
    }
    actions[position] = button
    page_manifest_path.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Add a Stream Deck button")
    parser.add_argument("--label", required=True)
    parser.add_argument("--folder", required=True)
    parser.add_argument("--color", default="#ffffff")
    parser.add_argument(
        "--command", default="continue", choices=["continue", "new", "resume", "prompt"]
    )
    parser.add_argument("--prompt", default=None)
    parser.add_argument(
        "--skip-permissions",
        action="store_true",
        help="OPT-IN, off by default: start Claude Code with --dangerously-skip-permissions "
        "so it runs commands and edits files without asking first.",
    )
    parser.add_argument("--position", default=None)
    parser.add_argument("--title", default=None)
    args = parser.parse_args()

    slug = safe_filename(args.label)

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    worker_bat = SCRIPTS_DIR / f"claude-{slug}-worker.bat"
    vbs_path = SCRIPTS_DIR / f"claude-{slug}.vbs"

    bat_lines = build_worker_bat_lines(
        args.folder, args.command, args.prompt, skip_permissions=args.skip_permissions
    )
    write_bat_crlf(worker_bat, bat_lines)
    write_vbs(vbs_path, build_vbs(worker_bat))

    page_manifest_path = find_current_page()

    data = json.loads(page_manifest_path.read_text(encoding="utf-8"))
    actions = get_keypad_actions(data)
    position = args.position or find_free_slot(actions)

    if args.command == "continue":
        default_title = f"{args.label}\n続きから"
    elif args.command == "new":
        default_title = f"{args.label}\n新規"
    elif args.command == "resume":
        default_title = f"{args.label}\n選択"
    else:
        default_title = args.label
    title = args.title or default_title

    insert_button(page_manifest_path, position, title, args.color, vbs_path)

    result = {
        "worker_bat": str(worker_bat),
        "vbs": str(vbs_path),
        "manifest": str(page_manifest_path),
        "position": position,
        "title": title,
        "color": args.color,
        "skip_permissions": args.skip_permissions,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
