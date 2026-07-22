"""RSSフィード構成と配信件数の設定。"""

# category は "politics_economy" (政治経済) または "tech" (テック系)
FEEDS = [
    {"name": "NHKニュース 政治", "url": "https://www3.nhk.or.jp/rss/news/cat4.xml", "category": "politics_economy"},
    {"name": "NHKニュース 経済", "url": "https://www3.nhk.or.jp/rss/news/cat5.xml", "category": "politics_economy"},

    {"name": "ITmedia AI+", "url": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml", "category": "tech"},
    {"name": "ITmedia NEWS", "url": "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml", "category": "tech"},
    {"name": "Publickey", "url": "https://www.publickey1.jp/atom.xml", "category": "tech"},
    {"name": "日経クロステック IT", "url": "https://xtech.nikkei.com/rss/xtech-it.rdf", "category": "tech"},
    {"name": "ZDNet Japan", "url": "https://feeds.japan.zdnet.com/rss/zdnet/all.rdf", "category": "tech"},
    {"name": "PC Watch", "url": "https://pc.watch.impress.co.jp/data/rss/1.0/pcw/feed.rdf", "category": "tech"},
    {"name": "ASCII.jp", "url": "https://ascii.jp/rss.xml", "category": "tech"},
    {"name": "マイナビニュース", "url": "https://news.mynavi.jp/rss/index.xml", "category": "tech"},
]

# テック系記事の優先度付けに使うキーワード(タイトルに含まれるほど上位に来る)
TECH_KEYWORDS = [
    "AI", "ai", "人工知能", "生成AI", "LLM", "ChatGPT", "Gemini", "Claude", "OpenAI",
    "ソフトウェア", "アプリ", "クラウド", "開発", "プログラ", "OSS", "オープンソース",
    "半導体", "チップ", "TSMC", "NVIDIA", "エヌビディア", "Intel", "インテル", "GPU", "SoC",
]

POLITICS_ECONOMY_COUNT = 5
TECH_COUNT = 15
TOTAL_COUNT = POLITICS_ECONOMY_COUNT + TECH_COUNT

# 一度配信した記事URLを何日間「既読」として重複配信を避けるか
HISTORY_RETENTION_DAYS = 3
HISTORY_FILE = "sent_history.json"

FETCH_TIMEOUT_SECONDS = 10
