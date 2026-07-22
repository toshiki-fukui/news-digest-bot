# ニュースダイジェスト配信bot

1日3回、Web全体(海外含む)を検索してニュースを選び、LINEに配信します。

- 政治・経済ニュース: 5件
- テック系ニュース: 15件 (AI・ソフトウェア・半導体を中心に、海外ソースも含めて選定)
- 合計 約20件/回
- 直近3日以内に配信済みの記事は重複配信しない (`sent_history.json` で管理)

## 仕組み(2段構成)

1. **記事選定 — Claude Code routine**
   PCの起動状態に関係なくクラウド上で1日3回起動し、Web検索(WebSearch/WebFetch)で
   国内外のニュースを探索。Sonnetが政治経済5件・テック15件を選び、要約とあわせて
   `pending_digest.json` に書き出し、`sent_history.json`(重複防止用の配信済みURL履歴)
   とともにこのリポジトリへコミット&プッシュする。

2. **配信 — GitHub Actions**
   `pending_digest.json` の変更をトリガーに `.github/workflows/send-digest.yml` が起動し、
   `LINE_CHANNEL_ACCESS_TOKEN`(GitHub Secretsで管理)を使ってLINEへ配信する。

この分離により、LINEのトークンはGitHub Secretsの外に一切出ない。

## セットアップ

### 1. 依存パッケージのインストール

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. LINE Messaging API の準備

LINE Notifyは2025年3月末に終了したため、LINE Messaging APIの「Broadcast(全友だち配信)」を使います。

1. [LINE Developers Console](https://developers.line.biz/) にログイン
2. 新規プロバイダー作成 → 「Messaging API」チャネルを作成
3. チャネル基本設定から「チャネルアクセストークン(長期)」を発行
4. 「Messaging API設定」タブのQRコードで、このBotを自分のLINEで友だち追加
   (自動応答・あいさつメッセージはオフにしておくと通知だけがシンプルに届きます)

### 3. トークンの設定

ローカルでの動作確認用:

```bash
cp .env.example .env
# .env を編集して LINE_CHANNEL_ACCESS_TOKEN に発行したトークンを貼り付け
```

本番配信用(GitHub Actions): リポジトリの Settings → Secrets and variables → Actions で
`LINE_CHANNEL_ACCESS_TOKEN` を登録(`gh secret set` でも可)。

### 4. 動作確認

```bash
# pending_digest.json の内容を確認するだけ(LINEには送らない)
.venv/bin/python3 main.py --dry-run

# 実際にLINEへ配信
.venv/bin/python3 main.py
```

### 5. Claude Code routine の設定(記事選定の自動化)

記事選定はローカルのcronではなく、[claude.ai](https://claude.ai/code/routines) 上のクラウドAgent(routine)が
1日3回(JST 7:00 / 12:00 / 19:00)起動して行う。

1. **GitHub連携を済ませる**
   claude.ai の GitHub連携は「OAuth認可(Authorized)」と「GitHub Appのインストール(Installed)」の
   2段階になっている。`github.com/settings/applications` の Authorized OAuth Apps には出ているのに
   `github.com/settings/installations` の Installed GitHub Apps に出てこない場合、インストールが
   完了していない(認可ポップアップだけ閉じてしまった等)。その場合は claude.ai 側のGitHub連携設定
   から再接続し、OAuth許可の後に出てくる **Install/Configure画面まで進めて**、対象リポジトリ
   (`news-digest-bot`)を明示的に選択する必要がある。
2. **routineを作成する**
   Claude Codeの `/schedule` コマンド(または https://claude.ai/code/routines の「New routine」)から、
   以下の内容で作成する。
   - リポジトリ: `https://github.com/toshiki-fukui/news-digest-bot`
   - モデル: `claude-sonnet-5`
   - 許可ツール: `Bash, Read, Write, Edit, Glob, Grep, WebSearch, WebFetch`
   - cron: `0 22,3,10 * * *`(UTC) = JST 7:00 / 12:00 / 19:00 毎日
   - プロンプト: WebSearch/WebFetchでニュースを探索し、政治経済5件・テック15件を選定して
     `pending_digest.json` を書き出し、`sent_history.json`(直近3日分の重複防止履歴)を更新して
     `main` ブランチへコミット&プッシュする、という内容(詳細は作成済みroutineの設定を参照)。
3. **routineの確認・編集・削除**
   一覧・実行ログの確認や削除は https://claude.ai/code/routines から行う(APIからの削除は不可)。
   即時実行して動作確認したい場合は「Run now」を使う。

### 6. GitHub Actions の設定(配信の自動化)

配信ワークフローは `.github/workflows/send-digest.yml` としてリポジトリに含まれており、
`pending_digest.json` の変更をpushしたタイミングで自動的に起動する(追加設定は不要)。
セットアップ時に必要なのは以下のSecret登録のみ。

```bash
gh secret set LINE_CHANNEL_ACCESS_TOKEN --body "<発行したチャネルアクセストークン>"
```

もしくはGitHubリポジトリの Settings → Secrets and variables → Actions から手動で登録してもよい。
登録後は、GitHubの「Actions」タブ → 「Send News Digest」→「Run workflow」から手動実行して
動作確認できる(直近の `pending_digest.json` の内容が再送信される)。

## データファイル

- `pending_digest.json` — routineが書き出す配信対象記事(選定のたびに上書き)
- `sent_history.json` — 配信済み記事URLと配信時刻(直近3日分)。重複配信を防ぐためroutineが管理する。

## 自動実行

- **記事選定**: Claude Code routine(JST 7:00 / 12:00 / 19:00、Sonnet + Web検索)
- **LINE配信**: GitHub Actions(`pending_digest.json` へのpushをトリガーに自動実行)

手動でテストしたい場合は、GitHubリポジトリの「Actions」タブ → 「Send News Digest」→
「Run workflow」で即時実行できます(直近の `pending_digest.json` の内容を再送信します)。
