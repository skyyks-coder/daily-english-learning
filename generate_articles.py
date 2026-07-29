import os
import json
import datetime
import requests
from openai import OpenAI

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY is missing.")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing.")

client = OpenAI(api_key=OPENAI_API_KEY)

today = datetime.datetime.utcnow().date()
from_date = today - datetime.timedelta(days=7)

DAY_TOPICS = {
    0: {
        "day": "Business",
        "query": "global business companies market strategy"
    },
    1: {
        "day": "Travel",
        "query": "travel tourism airlines hotels global destinations"
    },
    2: {
        "day": "AI",
        "query": "artificial intelligence AI technology business"
    },
    3: {
        "day": "Food",
        "query": "food restaurants dining global food industry"
    },
    4: {
        "day": "Economy",
        "query": "global economy inflation interest rates markets"
    },
    5: {
        "day": "Culture",
        "query": "culture arts film music entertainment global"
    },
    6: {
        "day": "Weekly Review",
        "query": "global business technology economy culture weekly news"
    }
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
        url = item.get("url") or ""
        source = item.get("source", {}).get("name") or "News Source"

        if title and description and url:
            return {
                "title": title,
                "description": description,
                "url": url,
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

Important:
- Do NOT reproduce the copyrighted full article.
- Create an original learning article based only on the title and description.
- The summary must be CEFR C1 level.
- Style should be professional, similar to Reuters Analysis, Financial Times, or The Economist.
- Use English only except Korean vocabulary meanings.
- Return valid JSON only.
- No markdown.
- No comments.

JSON structure:
{{
  "article": "An original study-friendly article of 8 to 12 paragraphs. It should explain the issue, background, possible implications, and useful English expressions. Do not copy the original article.",
  "summary": "A 15 to 20 sentence C1-level professional business-news style summary.",
  "vocabulary": [
    {{
      "word": "advanced English word",
      "meaning": "Korean meaning"
    }}
  ],
  "shadowing": [
    "Sentence 1 for speaking practice.",
    "Sentence 2 for speaking practice.",
    "Sentence 3 for speaking practice.",
    "Sentence 4 for speaking practice.",
    "Sentence 5 for speaking practice."
  ],
  "quiz": [
    {{
      "question": "Multiple choice question",
      "options": ["A", "B", "C", "D"],
      "answer": "Correct answer"
    }}
  ]
}}

Requirements:
- vocabulary: 8 items
- shadowing: 5 sentences
- quiz: 5 questions
- Summary must be sophisticated but readable.
- Avoid generic repeated sentences.
- Make the content directly related to the news topic.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You generate structured English learning content as valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content.strip()

    return json.loads(content)


def normalize_date(published_at):
    if not published_at:
        return today.isoformat()

    try:
        return published_at[:10]
    except Exception:
        return today.isoformat()


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
