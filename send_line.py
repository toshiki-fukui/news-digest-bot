"""LINE Messaging API (Broadcast) でニュースダイジェストを配信するモジュール。"""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

LINE_BROADCAST_URL = "https://api.line.me/v2/bot/message/broadcast"
MAX_TEXT_LENGTH = 4900  # LINEの1メッセージ上限(5000文字)に安全マージンを取る


def _format_section(title: str, entries: list) -> str:
    lines = [title]
    for i, e in enumerate(entries, start=1):
        summary = e.get("summary")
        detail = f"{summary}\n" if summary else ""
        lines.append(f"{i}. {e['title']}\n{detail}({e['source']}) {e['link']}")
    return "\n\n".join(lines)


def _compose(header: str, pe: list, tech: list, x_trending: list) -> str:
    blocks = [header]
    if pe:
        blocks.append(_format_section("■ 政治・経済", pe))
    if tech:
        blocks.append(_format_section("■ テック(AI/ソフトウェア/半導体 中心)", tech))
    if x_trending:
        blocks.append(_format_section("■ Xトレンド(テック)", x_trending))
    return "\n\n".join(blocks)


def _header(run_label: str, pe: list, tech: list, x_trending: list) -> str:
    return (
        f"【ニュースダイジェスト】{run_label}\n"
        f"政治経済 {len(pe)}件 / テック {len(tech)}件 / Xトレンド {len(x_trending)}件"
    )


def build_messages(news: dict, run_label: str) -> list:
    """news = {"politics_economy": [...], "tech": [...], "x_trending_tech": [...]} から
    LINE送信用メッセージ配列を作る。LINE公式アカウントの無料メッセージ数(月200通)に
    収まるよう、1回の配信につきメッセージは常に1通(単一のtext)にまとめる。
    """
    pe = news.get("politics_economy", [])
    tech = list(news.get("tech", []))
    x_trending = list(news.get("x_trending_tech", []))

    header = _header(run_label, pe, tech, x_trending)
    text = _compose(header, pe, tech, x_trending)

    # 文字数上限を超える場合は、優先度の低いものから末尾を削って収める(Xトレンド→テックの順)
    while len(text) > MAX_TEXT_LENGTH and (x_trending or tech):
        if x_trending:
            x_trending.pop()
        else:
            tech.pop()
        header = _header(run_label, pe, tech, x_trending)
        text = _compose(header, pe, tech, x_trending)

    return [{"type": "text", "text": text[:MAX_TEXT_LENGTH]}]


def broadcast(messages: list) -> None:
    token = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("環境変数 LINE_CHANNEL_ACCESS_TOKEN が設定されていません(.envを確認してください)")

    resp = requests.post(
        LINE_BROADCAST_URL,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={"messages": messages},
        timeout=10,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"LINE配信に失敗しました: {resp.status_code} {resp.text}")
