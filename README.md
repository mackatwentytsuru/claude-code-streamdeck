# claude-code-streamdeck

[English](#english) | [日本語](#日本語)

---

## English

A Claude Code plugin that adds **fully automated Stream Deck button creation** on Windows 11. Each button opens Claude Code in a folder of your choice.

It was built with Claude Code, and it is a Claude Code plugin itself: you ask in plain language, and a bundled skill does the work.

Say "Add a Stream Deck button that opens Claude Code in C:\projects\my-app" and Claude will:

1. Generate a worker `.bat` (ASCII + CRLF + `chcp 65001`)
2. Generate a launcher `.vbs`
3. Find the next free key on the active Stream Deck page
4. Add the button to that page's `manifest.json`
5. Restart the Stream Deck desktop app
6. Check that the button really opens a terminal window

No manual app restart, no manual button test, no JSON editing.

### Requirements

- Windows 11
- Elgato Stream Deck Plus (model `20GBD9901`)
- Stream Deck desktop app at its default location (`C:\Program Files\Elgato\StreamDeck\StreamDeck.exe`)
- Python 3.10 or newer on `PATH`
- Claude Code CLI on `PATH`
- PowerShell 5.1 or newer (built into Windows 11)

### Install

Inside Claude Code:

```text
/plugin marketplace add mackatwentytsuru/claude-code-streamdeck
/plugin install streamdeck-launcher@macka-streamdeck
```

The skill loads at session start. Claude uses it when you ask for a Stream Deck button.

Manual install without the marketplace:

```powershell
git clone https://github.com/mackatwentytsuru/claude-code-streamdeck "$env:USERPROFILE\.claude\plugins\streamdeck-launcher"
```

To update: `/plugin marketplace update macka-streamdeck`, then `/plugin update streamdeck-launcher`.

### Usage

Ask in natural language, in English or Japanese:

```text
Add a Stream Deck button that opens Claude Code in C:\projects\my-app
```

```text
DaVinciフォルダで続きから開くボタン追加して
```

Claude asks only for what is missing (folder, label, color, command type), picks a free key itself, creates the files, restarts Stream Deck and verifies the result.

### Command types

| Command | What the button runs |
|---------|----------------------|
| `continue` (default) | `claude --continue --dangerously-skip-permissions` |
| `new` | `claude --dangerously-skip-permissions` |
| `resume` | `claude --resume --dangerously-skip-permissions` |
| `prompt` | `claude -p "<your prompt>" --dangerously-skip-permissions` (non-interactive) |

### Security note: permission prompts are skipped

Every generated button starts Claude Code with `--dangerously-skip-permissions`. Claude can then run commands and edit files in that folder without asking you first. Use it only on folders and projects you trust. If you want the normal permission prompts, remove that flag from the generated `claude-<label>-worker.bat` (or from `build_worker_bat_lines` in `skills/add-streamdeck-button/scripts/create-button.py`).

### What gets created

For a button labeled `DaVinci`:

```text
%USERPROFILE%\StreamDeckScripts\
├── claude-davinci-worker.bat    # ASCII + CRLF + chcp 65001 + cd /d <folder> + claude
└── claude-davinci.vbs           # opens the worker in a visible cmd window
```

The active page's Stream Deck `manifest.json` gets a new `Open` action that points to the `.vbs`.

Why a `.vbs`? The Stream Deck `Open` action goes through `ShellExecute`. On Windows 11 that sends `.bat` files into Windows Terminal in a way that loses arguments. A small `.vbs` that starts `cmd /k worker.bat` reliably opens a visible terminal.

### Design choices

- No clipboard or paste automation. This keeps it compatible with voice-input tools that overwrite the clipboard.
- Batch files are ASCII + CRLF, so Japanese folder names do not break.
- Every worker `.bat` runs `chcp 65001` for UTF-8 console output.

### Limitations

- Windows 11 and Stream Deck Plus only. It was tested only on the author's machine. Other Stream Deck models may work, but the key layout (4x2) is assumed to be the Plus layout.
- Keypad buttons only. The dials (encoders) are not supported.
- It edits the Stream Deck profile `manifest.json` in place and does not make a backup. Back up `%APPDATA%\Elgato\StreamDeck\ProfilesV3` first if you care about your layout.
- It restarts the Stream Deck app. If the app does not close politely, the script force-kills it, so save anything open in the Stream Deck app first.
- It only works on the profile page that is currently active.

### License

MIT. See [LICENSE](LICENSE).

---

## 日本語

Windows 11 で、Stream Deck のボタンを**自動で作る** Claude Code のプラグインです。作ったボタンを押すと、決めたフォルダで Claude Code が開きます。

Claude Code で作りました。自分自身も Claude Code のプラグインで、ふつうの言葉でお願いすると、中のスキルが作業をします。

たとえば「C:\projects\my-app で Claude Code を開くボタンを追加して」と言うと、Claude は次のことをします。

1. 作業用の `.bat` を作る(ASCII・CRLF・`chcp 65001`)
2. 起動用の `.vbs` を作る
3. 今開いているページの、空いているキーを探す
4. そのページの `manifest.json` にボタンを足す
5. Stream Deck アプリを再起動する
6. ボタンで本当にターミナルが開くか確かめる

アプリを手で再起動する必要も、ボタンを押して試す必要も、JSON を書き換える必要もありません。

### 必要な物

- Windows 11
- Elgato Stream Deck Plus(型番 `20GBD9901`)
- 標準の場所に入っている Stream Deck アプリ(`C:\Program Files\Elgato\StreamDeck\StreamDeck.exe`)
- `PATH` の通った Python 3.10 以上
- `PATH` の通った Claude Code(CLI)
- PowerShell 5.1 以上(Windows 11 に最初から入っています)

### 入れ方

Claude Code の中で次を打ちます。

```text
/plugin marketplace add mackatwentytsuru/claude-code-streamdeck
/plugin install streamdeck-launcher@macka-streamdeck
```

セッションの始まりにスキルが読み込まれ、Stream Deck のボタンをお願いしたときに使われます。

マーケットプレイスを使わない入れ方:

```powershell
git clone https://github.com/mackatwentytsuru/claude-code-streamdeck "$env:USERPROFILE\.claude\plugins\streamdeck-launcher"
```

更新するときは、`/plugin marketplace update macka-streamdeck` のあとに `/plugin update streamdeck-launcher` を打ちます。

### 使い方

英語でも日本語でも、ふつうの言葉でお願いします。

```text
DaVinciフォルダで続きから開くボタン追加して
```

```text
Add a Stream Deck button that opens Claude Code in C:\projects\my-app
```

足りないこと(フォルダ・名前・色・種類)だけを聞かれます。キーの場所は自動で選ばれ、ファイルの作成・再起動・確認まで行われます。

### 種類(command)

| command | ボタンで動くもの |
|---------|------------------|
| `continue`(初期値) | `claude --continue --dangerously-skip-permissions` |
| `new` | `claude --dangerously-skip-permissions` |
| `resume` | `claude --resume --dangerously-skip-permissions` |
| `prompt` | `claude -p "<指示>" --dangerously-skip-permissions`(対話なし) |

### 安全についての注意: 確認なしで動きます

作られるボタンは、すべて `--dangerously-skip-permissions` を付けて Claude Code を起動します。つまり、そのフォルダの中で、Claude が確認なしにコマンドを動かし、ファイルを書き換えます。信頼できるフォルダ・プロジェクトにだけ使ってください。ふつうの確認を出したいときは、作られた `claude-<名前>-worker.bat`(または `skills/add-streamdeck-button/scripts/create-button.py` の `build_worker_bat_lines`)から、この印を消してください。

### 作られるもの

`DaVinci` という名前のボタンの場合:

```text
%USERPROFILE%\StreamDeckScripts\
├── claude-davinci-worker.bat    # ASCII + CRLF + chcp 65001 + cd /d <フォルダ> + claude
└── claude-davinci.vbs           # 作業用 bat を、見えるコマンド窓で開く
```

今開いているページの `manifest.json` に、`.vbs` を指す `Open` の動作が1つ足されます。

なぜ `.vbs` か: Stream Deck の `Open` は `ShellExecute` を通ります。Windows 11 では `.bat` が Windows Terminal に回されて、引数が落ちることがあります。`cmd /k worker.bat` を起こす小さな `.vbs` をはさむと、確実に見える窓が開きます。

### 作りの決まり

- クリップボードや貼り付けの自動操作はしません(クリップボードを書き換える音声入力のツールと一緒に使えます)。
- bat は ASCII + CRLF なので、日本語のフォルダ名でも壊れません。
- どの作業用 bat にも `chcp 65001` が入っていて、画面は UTF-8 になります。

### できないこと・気をつけること

- Windows 11 と Stream Deck Plus だけです。動作を確かめたのは作者の機械だけです。ほかの Stream Deck でも動くかもしれませんが、キーの並び(4x2)は Plus のものと決めています。
- キー(ボタン)だけです。ダイヤル(エンコーダー)には対応していません。
- Stream Deck のプロファイル `manifest.json` を直接書き換え、バックアップは作りません。配置が大事なら、先に `%APPDATA%\Elgato\StreamDeck\ProfilesV3` を写しておいてください。
- Stream Deck アプリを再起動します。静かに閉じないときは強制終了するので、アプリで作業中のものは先に保存してください。
- いま開いているページにだけ作用します。

### ライセンス

MIT です。[LICENSE](LICENSE) を見てください。
