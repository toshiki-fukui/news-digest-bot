"""ニュースダイジェストのLINE配信エントリーポイント。

記事の選定はClaude Code routine(Web検索 + Sonnet)がこのリポジトリの
pending_digest.json に書き出す形で行う。このスクリプトはその結果を読み込んで
LINEへ配信するだけの役割。

使い方:
    python3 main.py           # 実際にLINEへ配信
    python3 main.py --dry-run # 配信はせず、内容を標準出力に表示するだけ
"""

import json
import os
import sys

from send_line import build_messages, broadcast

PENDING_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pending_digest.json")


def load_pending() -> dict:
    if not os.path.exists(PENDING_PATH):
        return {}
    with open(PENDING_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    news = load_pending()
    pe = news.get("politics_economy", [])
    tech = news.get("tech", [])
    run_label = news.get("run_label", "")

    if not pe and not tech:
        print("pending_digest.json が空、または存在しません。配信をスキップします。")
        return 0

    messages = build_messages(news, run_label)

    if dry_run:
        for m in messages:
            print(m["text"])
            print("-" * 40)
        return 0

    broadcast(messages)
    print(f"配信完了: 政治経済 {len(pe)}件 / テック {len(tech)}件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
