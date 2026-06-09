---
name: add-streamdeck-button
description: Add a button to an Elgato Stream Deck Plus (Windows 11) that launches Claude Code in a specified folder. Fully automated end-to-end - no manual app restart or testing required. Use when the user asks to add/create/make a Stream Deck button, especially for launching Claude Code in a folder, or for a specific terminal command.
---

# Add Stream Deck Button (Fully Automated)

## When to invoke

The user says any of:
- "ストリームデックにボタン追加して"
- "X フォルダで Claude を開くボタン作って"
- "X 続きから/新規/選択 ボタン追加"
- "Add a Stream Deck button for X"

## Inputs to collect

If not specified, ask in ONE round:
- **label** (short name, e.g., "DaVinci", "Resolume") - required
- **folder** (absolute Windows path) - required
- **command** (`continue` / `new` / `resume` / `prompt`) - default `continue`
- **color** (hex like `#fbbf24`) - default `#ffffff`, suggest a fitting color
- **prompt** (only if command=prompt) - the text to pass to `claude -p`

Do NOT ask about: position (auto-detect free slot), title (auto-generate from label+command), page (always the currently active page).

## Constraints (CRITICAL)

1. **NEVER use clipboard/paste** in any generated automation. If the user uses voice input tools (e.g. Aqua Voice) that clobber the clipboard, paste-based automation breaks. Use direct cmd execution only.
2. **Worker bat files MUST be ASCII + CRLF + `chcp 65001 >nul 2>&1`** to handle Japanese paths safely.
3. **The user should NOT have to restart Stream Deck manually** - the skill handles it.
4. **The user should NOT have to press the button to test it** - the skill verifies it.

## Execution flow

Run these steps in order with Bash. Do NOT skip steps. Do NOT ask the user to do anything between steps.

The plugin root is available as `${CLAUDE_PLUGIN_ROOT}`. All scripts live under `${CLAUDE_PLUGIN_ROOT}/skills/add-streamdeck-button/scripts/`.

### Step 1: Create button files + edit manifest

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/add-streamdeck-button/scripts/create-button.py" \
    --label "<LABEL>" \
    --folder "<FOLDER>" \
    --color "<COLOR>" \
    --command "<COMMAND>"
```

Capture the JSON output to know the worker_bat / vbs / position created.

For `--command prompt`, also pass `--prompt "<PROMPT_TEXT>"`.

### Step 2: Restart Stream Deck automatically

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File \
    "${CLAUDE_PLUGIN_ROOT}/skills/add-streamdeck-button/scripts/restart-streamdeck.ps1"
```

Wait for "Stream Deck running" confirmation in output. Allow ~10s for SD to fully load the new profile.

```bash
sleep 8
```

### Step 3: Verify the button works

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/add-streamdeck-button/scripts/verify-button.py" \
    --vbs "<VBS_PATH_FROM_STEP_1>" \
    --timeout 15
```

This launches the VBS directly (same as the button would) and detects the new terminal window. Output JSON has `ok: true` if a console window appeared.

### Step 4: Report to user

Present a compact summary:
- Position assigned (e.g., "0,1 = 左下")
- Folder + command
- Verification result (window detected / not detected)
- If verification failed, troubleshoot using `claude -p` directly in the folder

## Position naming for user-friendly reports

Stream Deck Plus is 4x2 grid. Map `col,row` to readable position:

| col,row | 位置 |
|--------|------|
| 0,0    | 左上 |
| 1,0    | 上段2 |
| 2,0    | 上段3 |
| 3,0    | 右上 |
| 0,1    | 左下 |
| 1,1    | 下段2 |
| 2,1    | 下段3 |
| 3,1    | 右下 |

## Color suggestions by purpose

| Use case | Hex |
|----------|-----|
| Default / neutral | `#ffffff` |
| Continue (default) | `#a855f7` (purple) |
| Video/Color (DaVinci) | `#fbbf24` (amber) |
| Lighting (QLC+) | `#00d4ff` (cyan) |
| Code (ECC) | `#22c55e` (green) |
| VJ (Resolume) | `#ef4444` (red) |
| Audio | `#3b82f6` (blue) |

## Failure recovery

If Step 3 reports `ok: false`:
- Check the worker bat encoding: `file %USERPROFILE%\StreamDeckScripts\claude-<slug>-worker.bat` should report "ASCII text, with CRLF line terminators"
- Test the bat directly: `cmd.exe /c "%USERPROFILE%\StreamDeckScripts\claude-<slug>-worker.bat"` should produce no encoding error
- If the manifest write didn't take effect, ensure Step 2 (restart) actually completed by re-running it.

If Stream Deck won't restart cleanly:
- The PowerShell script does graceful close → force kill → wait → relaunch. If it still fails, check `Get-Process StreamDeck` manually.

## Notes for future button types

- **Encoder buttons (dials on SD Plus)**: not supported in this skill version; use Stream Deck app GUI.
- **Multi-action sequences**: use `command=prompt` for a single prompt; for multi-step sequences, build a custom worker bat that pipes stdin.
- **Other languages**: extend `--command` choices in `create-button.py`.

## Requirements

- Windows 11
- Elgato Stream Deck Plus (model `20GBD9901`)
- Elgato Stream Deck desktop app installed at default location
- Python 3.10+
- Claude Code CLI installed and on PATH
- PowerShell 5.1+ (built-in on Windows 11)
