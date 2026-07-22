# ニュースダイジェスト配信bot

1日4回、RSSフィードから最新ニュースを集めてLINEに配信します。

- 政治・経済ニュース: 5件 (NHKニュース 政治/経済)
- テック系ニュース: 15件 (AI・ソフトウェア・半導体を中心にキーワードで優先度付け)
- 合計 約20件/回
- 直近3日以内に配信済みの記事は重複配信しない (`sent_history.json` で管理)

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

```bash
cp .env.example .env
# .env を編集して LINE_CHANNEL_ACCESS_TOKEN に発行したトークンを貼り付け
```

### 4. 動作確認

```bash
# LINEには送らず内容を確認するだけ
.venv/bin/python3 main.py --dry-run

# 実際にLINEへ配信
.venv/bin/python3 main.py
```

## 配信対象フィードの調整

`config.py` の `FEEDS` にRSS URLを追加/削除できます。テック記事の優先キーワードは `TECH_KEYWORDS` で調整できます。

## 1日4回の自動実行 (GitHub Actions)

`.github/workflows/news-digest.yml` がGitHub Actions上でJST 7:00 / 12:00 / 18:00 / 22:00に実行されるよう設定されています。PCを起動していなくても配信されます。

- 実行時刻を変えたい場合は、ワークフロー内の `cron` (UTC) を編集してください。JST = UTC+9です。
- 重複配信を避けるための `sent_history.json` は、実行のたびにActionsが自動でコミット&プッシュして更新します。
- GitHub Actionsの無料枠(privateリポジトリで月2,000分)で十分収まる軽量な処理です。

### 必要なSecrets設定

リポジトリの Settings → Secrets and variables → Actions で以下を登録してください(CLIから設定済みの場合は不要):

- `LINE_CHANNEL_ACCESS_TOKEN`: LINE Messaging APIのチャネルアクセストークン(長期)

### 手動実行

GitHubリポジトリの「Actions」タブ → 「News Digest」ワークフロー → 「Run workflow」で、スケジュールを待たずに即時実行できます。
