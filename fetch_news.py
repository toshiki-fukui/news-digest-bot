"""RSSフィードを取得し、カテゴリ別に上位記事を選定するモジュール。"""

import json
import os
import time
from datetime import datetime, timedelta, timezone

import feedparser
import requests

import config

JST = timezone(timedelta(hours=9))
HISTORY_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), config.HISTORY_FILE)


def load_history() -> dict:
    if not os.path.exists(HISTORY_PATH):
        return {}
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def prune_history(history: dict) -> dict:
    cutoff = time.time() - config.HISTORY_RETENTION_DAYS * 86400
    return {url: ts for url, ts in history.items() if ts >= cutoff}


def save_history(history: dict) -> None:
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def fetch_feed(feed_conf: dict) -> list:
    """1フィードを取得してエントリのリストを返す。失敗時は空リスト。"""
    try:
        resp = requests.get(
            feed_conf["url"],
            timeout=config.FETCH_TIMEOUT_SECONDS,
            headers={"User-Agent": "Mozilla/5.0 (news-digest-bot)"},
        )
        resp.raise_for_status()
        parsed = feedparser.parse(resp.content)
    except (requests.RequestException, Exception):
        return []

    entries = []
    for e in parsed.entries:
        title = e.get("title", "").strip()
        link = e.get("link", "").strip()
        if not title or not link:
            continue
        published_struct = e.get("published_parsed") or e.get("updated_parsed")
        if published_struct:
            published = datetime.fromtimestamp(time.mktime(published_struct), tz=timezone.utc)
        else:
            published = datetime.now(tz=timezone.utc)
        entries.append({
            "title": title,
            "link": link,
            "source": feed_conf["name"],
            "category": feed_conf["category"],
            "published": published,
        })
    return entries


def tech_score(title: str) -> int:
    return sum(1 for kw in config.TECH_KEYWORDS if kw.lower() in title.lower())


def collect_news() -> dict:
    """全フィードを取得し、政治経済/テックそれぞれ上位記事を選んで返す。
    戻り値: {"politics_economy": [entry, ...], "tech": [entry, ...]}
    """
    history = prune_history(load_history())

    politics_economy_pool = []
    tech_pool = []
    seen_links = set()

    for feed_conf in config.FEEDS:
        for entry in fetch_feed(feed_conf):
            if entry["link"] in history or entry["link"] in seen_links:
                continue
            seen_links.add(entry["link"])
            if entry["category"] == "politics_economy":
                politics_economy_pool.append(entry)
            else:
                tech_pool.append(entry)

    politics_economy_pool.sort(key=lambda e: e["published"], reverse=True)
    selected_pe = politics_economy_pool[:config.POLITICS_ECONOMY_COUNT]

    tech_pool.sort(key=lambda e: (tech_score(e["title"]), e["published"]), reverse=True)
    selected_tech = tech_pool[:config.TECH_COUNT]

    now_ts = time.time()
    for entry in selected_pe + selected_tech:
        history[entry["link"]] = now_ts
    save_history(history)

    return {"politics_economy": selected_pe, "tech": selected_tech}
