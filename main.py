"""1日4回のニュースダイジェスト配信のエントリーポイント。

使い方:
    python3 main.py           # 実際にLINEへ配信
    python3 main.py --dry-run # 配信はせず、内容を標準出力に表示するだけ
"""

import sys
from datetime import datetime, timezone, timedelta

from fetch_news import collect_news
from send_line import build_messages, broadcast

JST = timezone(timedelta(hours=9))


def run_label(now: datetime) -> str:
    return now.strftime("%m/%d %H:%M")


def main() -> int:
    dry_run = "--dry-run" in sys.argv

    now = datetime.now(tz=JST)
    news = collect_news()
    messages = build_messages(news, run_label(now))

    total = len(news.get("politics_economy", [])) + len(news.get("tech", []))
    if total == 0:
        print("新着記事なし(直近の配信済み履歴と重複、または取得失敗)。配信をスキップします。")
        return 0

    if dry_run:
        for m in messages:
            print(m["text"])
            print("-" * 40)
        return 0

    broadcast(messages)
    print(f"配信完了: 政治経済 {len(news['politics_economy'])}件 / テック {len(news['tech'])}件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
