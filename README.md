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

| Command | What the button runs (default) | With the opt-in `--skip-permissions` |
|---------|--------------------------------|--------------------------------------|
| `continue` (default) | `claude --continue` | `claude --continue --dangerously-skip-permissions` |
| `new` | `claude` | `claude --dangerously-skip-permissions` |
| `resume` | `claude --resume` | `claude --resume --dangerously-skip-permissions` |
| `prompt` | `claude -p "<your prompt>"` (non-interactive) | `claude -p "<your prompt>" --dangerously-skip-permissions` |

### Safe by default: Claude asks before it acts

By default a button starts Claude Code normally. Claude asks you before it runs a command or edits a file, as it does when you start it by hand. Note that `prompt` buttons are non-interactive: nobody is there to answer, so any tool that needs approval is refused unless you use the opt-in below.

### Opt-in: skip the confirmations (risky)

If you want a button that never asks, say so when you ask for it ("... and skip the permission prompts"), or pass `--skip-permissions` to `create-button.py`. The worker `.bat` then starts Claude Code with `--dangerously-skip-permissions`.

What that means: Claude can run any command and change or delete any file the folder and your account allow, without asking you first. A mistake, or a malicious instruction hidden in a file or web page that Claude reads, can do real damage. Use it only on folders and projects you trust, ideally with a backup or version control. It is chosen per button; it is never turned on automatically. To switch a button back, delete ` --dangerously-skip-permissions` from its `claude-<label>-worker.bat`, or create the button again without the option.

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

### Tests

```bash
python -m pip install pytest
python -m pytest tests
```

The tests only call the pure functions and `--help`. They write to a temporary folder, never to your Stream Deck profile or `StreamDeckScripts` folder.

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

| command | ボタンで動くもの(初期値) | 選んだとき(`--skip-permissions`) |
|---------|--------------------------|-------------------------------------|
| `continue`(初期値) | `claude --continue` | `claude --continue --dangerously-skip-permissions` |
| `new` | `claude` | `claude --dangerously-skip-permissions` |
| `resume` | `claude --resume` | `claude --resume --dangerously-skip-permissions` |
| `prompt` | `claude -p "<指示>"`(対話なし) | `claude -p "<指示>" --dangerously-skip-permissions` |

### 初期値は安全: 実行の前に Claude が確認します

ボタンは、ふつうに Claude Code を起動します。コマンドを動かすときやファイルを書き換えるときは、自分で起動したときと同じように、Claude が先に確認します。ただし `prompt` のボタンは対話なしで動くので、答える人がおらず、確認が要る道具は断られます(下の「選ぶ設定」を使わない限り)。

### 選ぶ設定: 確認を飛ばす(危険があります)

確認なしで動くボタンが欲しいときは、お願いするときに「確認を飛ばして」と伝えるか、`create-button.py` に `--skip-permissions` を付けます。すると作業用の `.bat` が `--dangerously-skip-permissions` 付きで Claude Code を起動します。

意味: そのフォルダとあなたのアカウントが許す範囲で、Claude が、確認なしに、どんなコマンドでも動かし、どんなファイルでも書き換えたり消したりできます。間違いや、Claude が読むファイル・Web ページに隠された悪意のある指示で、本当に被害が出ることがあります。信頼できるフォルダ・プロジェクトにだけ、できればバックアップやバージョン管理のある状態で使ってください。ボタンごとに選ぶ設定で、自動では決して有効になりません。戻すには、`claude-<名前>-worker.bat` の ` --dangerously-skip-permissions` を消すか、オプションなしでボタンを作り直します。

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

### テスト

```bash
python -m pip install pytest
python -m pytest tests
```

テストが呼ぶのは、中の関数と `--help` だけです。書き込み先は一時フォルダで、Stream Deck のプロファイルや `StreamDeckScripts` フォルダには決して書き込みません。

### ライセンス

MIT です。[LICENSE](LICENSE) を見てください。

---

### Author / 作者

Made by Yuki Tsuruoka — stage visuals and live show production, building tools with Claude Code. Web: [otolume.com](https://otolume.com) (OTOLUME, a stage LED visual service) / Instagram: [@tsuru614](https://www.instagram.com/tsuru614/) / YouTube: [channel](https://www.youtube.com/channel/UCYngpwyo7vGBIXBtKhh7z1g)

作者: Yuki Tsuruoka(ステージ映像・ライブ演出。道具は Claude Code で作っています)Web: [otolume.com](https://otolume.com)(OTOLUME、ステージ LED 映像のサービス) / Instagram: [@tsuru614](https://www.instagram.com/tsuru614/) / YouTube: [channel](https://www.youtube.com/channel/UCYngpwyo7vGBIXBtKhh7z1g)