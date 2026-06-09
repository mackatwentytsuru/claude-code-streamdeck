"""Verify a Stream Deck button by launching its VBS and detecting the window.

Usage:
    python verify-button.py --vbs C:\\path\\to\\claude-davinci.vbs
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def list_console_windows() -> list[dict]:
    ps_script = r"""
Add-Type @"
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Text;

public class W {
    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern int GetWindowTextLength(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);

    public static List<string> List() {
        var result = new List<string>();
        EnumWindows((hWnd, _) => {
            if (!IsWindowVisible(hWnd)) return true;
            int len = GetWindowTextLength(hWnd);
            if (len == 0) return true;
            var sb = new StringBuilder(len + 1);
            GetWindowText(hWnd, sb, sb.Capacity);
            uint pid;
            GetWindowThreadProcessId(hWnd, out pid);
            try {
                var p = Process.GetProcessById((int)pid);
                result.Add(p.ProcessName + "|" + sb.ToString());
            } catch {}
            return true;
        }, IntPtr.Zero);
        return result;
    }
}
"@
[W]::List() | ForEach-Object { Write-Output $_ }
"""
    proc = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True,
    )
    raw = proc.stdout or b""
    text = ""
    for enc in ("utf-8", "cp932", "cp1252"):
        try:
            text = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if not text:
        text = raw.decode("utf-8", errors="replace")
    windows = []
    for line in text.splitlines():
        if "|" in line:
            name, title = line.split("|", 1)
            windows.append({"process": name.strip(), "title": title.strip()})
    return windows


def find_target_window(before: list[dict]) -> dict | None:
    after = list_console_windows()
    before_set = {(w["process"], w["title"]) for w in before}
    new_windows = [w for w in after if (w["process"], w["title"]) not in before_set]
    console_names = {"cmd", "conhost", "WindowsTerminal", "OpenConsole"}
    for w in new_windows:
        if w["process"] in console_names:
            return w
    if new_windows:
        return new_windows[0]
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vbs", required=True)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--no-launch", action="store_true")
    args = parser.parse_args()

    vbs_path = Path(args.vbs)
    if not vbs_path.exists():
        print(json.dumps({"ok": False, "error": f"VBS not found: {vbs_path}"}))
        return 1

    before = list_console_windows()

    if not args.no_launch:
        subprocess.Popen(
            ["wscript.exe", str(vbs_path)],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )

    found: dict | None = None
    for _ in range(args.timeout):
        time.sleep(1)
        found = find_target_window(before)
        if found:
            break

    verdict = {
        "ok": found is not None,
        "vbs": str(vbs_path),
        "window": found,
        "windows_after": len(list_console_windows()),
    }
    print(json.dumps(verdict, ensure_ascii=False, indent=2))
    return 0 if found else 2


if __name__ == "__main__":
    sys.exit(main())
