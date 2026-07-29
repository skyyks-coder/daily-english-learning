import os
import json
import datetime
import requests
import google.generativeai as genai

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY is missing.")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

today = datetime.datetime.utcnow().date()
from_date = today - datetime.timedelta(days=7)

DAY_TOPICS = {
    0: {"day": "Business", "query": "global business companies market strategy"},
    1: {"day": "Travel", "query": "travel tourism airlines hotels global destinations"},
    2: {"day": "AI", "query": "artificial intelligence AI technology business"},
    3: {"day": "Food", "query": "food restaurants dining global food industry"},
    4: {"day": "Economy", "query": "global economy inflation interest rates markets"},
    5: {"day": "Culture", "query": "culture arts film music entertainment global"},
    6: {"day": "Weekly Review", "query": "global business technology economy culture weekly news"}
}


def get_today_topic():
    weekday = datetime.datetime.utcnow().weekday()
    return DAY_TOPICS[weekday]


def fetch_news(topic_info):
    url = "https://newsapi.org/v2/everything"

    params = {
        "q": topic_info["query"],
        "language": "en",
        "sortBy": "publishedAt",
        "from": from_date.isoformat(),
        "pageSize": 10,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    articles = data.get("articles", [])

    if not articles:
        raise Exception("No articles found from NewsAPI.")

    for item in articles:
        title = item.get("title") or ""
        description = item.get("description") or ""
        article_url = item.get("url") or ""
        source = item.get("source", {}).get("name") or "News Source"

        if title and description and article_url:
            return {
                "title": title,
                "description": description,
                "url": article_url,
                "source": source,
                "publishedAt": item.get("publishedAt", "")
            }

    raise Exception("No valid article found.")


def generate_learning_content(news, topic):
    prompt = f"""
You are creating content for an English learning web app called Daily English Learning.

Topic: {topic}
News title: {news["title"]}
News source: {news["source"]}
News description: {news["description"]}
Original link: {news["url"]}

Return VALID JSON ONLY.

JSON structure:
{{
  "article": "",
  "summary": "",
  "vocabulary": [
    {{
      "word": "",
      "meaning": ""
    }}
  ],
  "shadowing": [],
  "quiz": [
    {{
      "question": "",
      "options": ["A","B","C","D"],
      "answer": ""
    }}
  ]
}}

Requirements:
- article: 8-12 paragraphs
- summary: 15-20 sentences
- vocabulary: 8 items
- shadowing: 5 items
- quiz: 5 questions
- CEFR C1 English
- Business-news style
- No markdown
- JSON only
"""

    response = model.generate_content(prompt)

    content = response.text.strip()

    if content.startswith("```json"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    return json.loads(content)


def normalize_date(published_at):
    if not published_at:
        return today.isoformat()

    return published_at[:10]


def main():
    topic_info = get_today_topic()
    topic = topic_info["day"]

    news = fetch_news(topic_info)
    learning = generate_learning_content(news, topic)

    article = {
        "day": topic,
        "title": news["title"],
        "source": news["source"],
        "date": normalize_date(news["publishedAt"]),
        "url": news["url"],
        "article": learning.get("article", ""),
        "summary": learning.get("summary", ""),
        "vocabulary": learning.get("vocabulary", []),
        "shadowing": learning.get("shadowing", []),
        "quiz": learning.get("quiz", [])
    }

    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump([article], f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
