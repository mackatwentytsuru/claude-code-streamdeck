"""Tests for the worker .bat generation in create-button.py.

These tests only call pure functions and `--help`. They never write to the real
Stream Deck profile or to the user's StreamDeckScripts folder: SCRIPTS_DIR is
redirected to a temporary directory.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "add-streamdeck-button"
    / "scripts"
    / "create-button.py"
)


@pytest.fixture()
def cb(tmp_path, monkeypatch):
    # The module builds a path from %APPDATA% at import time (it does not create it).
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    spec = importlib.util.spec_from_file_location("create_button", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "SCRIPTS_DIR", tmp_path / "StreamDeckScripts")
    return module


def claude_lines(lines):
    return [line for line in lines if line.startswith("claude")]


@pytest.mark.parametrize("command", ["continue", "new", "resume"])
def test_default_asks_before_acting(cb, command):
    lines = cb.build_worker_bat_lines("C:\\projects\\my-app", command, None)
    assert len(claude_lines(lines)) == 1
    assert "dangerously" not in "\n".join(lines)


def test_default_prompt_mode_has_no_skip_flag(cb):
    lines = cb.build_worker_bat_lines("C:\\projects\\my-app", "prompt", "hello")
    assert claude_lines(lines) == ['claude -p "%PROMPT%"']
    assert "dangerously" not in "\n".join(lines)


@pytest.mark.parametrize(
    "command, expected",
    [
        ("continue", "claude --continue --dangerously-skip-permissions"),
        ("new", "claude --dangerously-skip-permissions"),
        ("resume", "claude --resume --dangerously-skip-permissions"),
    ],
)
def test_opt_in_adds_the_flag(cb, command, expected):
    lines = cb.build_worker_bat_lines(
        "C:\\projects\\my-app", command, None, skip_permissions=True
    )
    assert claude_lines(lines) == [expected]


def test_opt_in_prompt_mode(cb):
    lines = cb.build_worker_bat_lines(
        "C:\\projects\\my-app", "prompt", "hello", skip_permissions=True
    )
    assert claude_lines(lines) == ['claude -p "%PROMPT%" --dangerously-skip-permissions']


def test_prompt_file_goes_to_the_redirected_folder(cb, tmp_path):
    cb.build_worker_bat_lines("C:\\projects\\my-app", "prompt", "hello")
    assert list((tmp_path / "StreamDeckScripts" / "prompts").glob("*.txt"))


def test_worker_bat_keeps_folder_and_utf8_codepage(cb):
    lines = cb.build_worker_bat_lines("C:\\projects\\my-app", "continue", None)
    assert lines[0] == "@echo off"
    assert lines[1].startswith("chcp 65001")
    assert lines[2] == 'cd /d "C:\\projects\\my-app"'


def test_bad_input_is_rejected(cb):
    with pytest.raises(ValueError):
        cb.build_worker_bat_lines("C:\\x", "prompt", None)
    with pytest.raises(ValueError):
        cb.build_worker_bat_lines("C:\\x", "bogus", None)


def test_cli_documents_the_opt_in_and_is_off_by_default():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
        env={**os.environ, "APPDATA": os.environ.get("TEMP", ".")},
        timeout=30,
    )
    assert result.returncode == 0
    assert "--skip-permissions" in result.stdout
    assert "OPT-IN" in result.stdout
