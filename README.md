# claude-code-streamdeck

A Claude Code plugin that adds **fully automated Stream Deck button creation** for launching Claude Code in any folder on Windows 11.

Just say "DaVinciフォルダで続きから開くボタン追加して" and Claude:

1. Generates the worker `.bat` (ASCII + CRLF + `chcp 65001`)
2. Generates the launcher `.vbs`
3. Detects the next free slot on the active page
4. Edits the Stream Deck `manifest.json`
5. Restarts the Stream Deck desktop app
6. Verifies the button actually opens a terminal

No manual app restart. No manual button-press test. No JSON editing.

## Requirements

- **Windows 11**
- **Elgato Stream Deck Plus** (model `20GBD9901`)
- **Stream Deck desktop app** installed at default location (`C:\Program Files\Elgato\StreamDeck\StreamDeck.exe`)
- **Python 3.10+** on `PATH`
- **Claude Code CLI** installed and on `PATH`
- **PowerShell 5.1+** (built-in on Windows 11)

Tested only with Stream Deck Plus. Other models may work but the layout assumptions (4x2 keypad) are Plus-specific.

## Install

### 1. Add this repo as a marketplace

```bash
/plugin marketplace add mackatwentytsuru/claude-code-streamdeck
```

### 2. Install the plugin

```bash
/plugin install streamdeck-launcher@macka-streamdeck
```

That's it. The skill auto-loads on session start, and Claude will detect when you ask for a Stream Deck button.

## Usage

Just ask in natural language:

```
DaVinciフォルダで続きから開くボタン追加して
```

```
Add a Stream Deck button that opens Claude Code in C:\projects\my-app
```

Claude will:
- Ask for any missing inputs (folder, color, command type)
- Auto-pick a free slot on the active page
- Generate scripts, edit the manifest
- Restart Stream Deck and verify the new button works

## Command types

| Command | What it runs |
|---------|--------------|
| `continue` (default) | `claude --continue --dangerously-skip-permissions` |
| `new` | `claude --dangerously-skip-permissions` |
| `resume` | `claude --resume --dangerously-skip-permissions` |
| `prompt` | `claude -p "<your prompt>" --dangerously-skip-permissions` (non-interactive) |

## What gets created

For a button labeled `DaVinci`:

```
%USERPROFILE%\StreamDeckScripts\
├── claude-davinci-worker.bat    # ASCII + CRLF + chcp 65001 + cd /d folder + claude
└── claude-davinci.vbs            # Launches the worker bat in a visible cmd window
```

The Stream Deck `manifest.json` for the active page gets a new `Open` action pointing to the `.vbs`.

## Why VBS instead of direct .bat?

Stream Deck's `Open` action goes through `ShellExecute`, which on Windows 11 routes `.bat` files into Windows Terminal in a way that loses arguments. A `.vbs` wrapper spawning `cmd /k worker.bat` reliably opens a visible terminal window.

## Constraints baked in

- **No clipboard/paste** automation (compatible with voice input tools that clobber the clipboard, e.g. Aqua Voice)
- **ASCII + CRLF batch files** so Japanese path encoding never breaks
- **`chcp 65001`** in every worker bat for UTF-8 console output

## Updating

```bash
/plugin marketplace update macka-streamdeck
/plugin update streamdeck-launcher
```

## Manual install (without marketplace)

If you don't want to use the marketplace:

```powershell
git clone https://github.com/mackatwentytsuru/claude-code-streamdeck "$env:USERPROFILE\.claude\plugins\streamdeck-launcher"
```

Claude Code picks up plugins under `~/.claude/plugins/` automatically on the next session.

## License

MIT
