import os
import json
import datetime
import requests
from openai import OpenAI

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY is missing.")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is missing.")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

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
        published_at = item.get("publishedAt", "")

        if title and description and article_url:
            return {
                "title": title,
                "description": description,
                "url": article_url,
                "source": source,
                "publishedAt": published_at
            }

    raise Exception("No valid article found.")


def clean_json_text(text):
    content = text.strip()

    if content.startswith("```json"):
        content = content.replace("```json", "", 1).strip()

    if content.startswith("```"):
        content = content.replace("```", "", 1).strip()

    if content.endswith("```"):
        content = content[:-3].strip()

    start = content.find("{")
    end = content.rfind("}")

    if start != -1 and end != -1:
        content = content[start:end + 1]

    return content


def generate_learning_content(news, topic):
    prompt = f"""
You are creating content for an English learning web app called Daily English Learning.

Use ONLY the information below.
Do NOT copy the original article.
Do NOT reproduce copyrighted text.
Create original English-learning content based on the title and description.

Topic category: {topic}
News title: {news["title"]}
News source: {news["source"]}
News description: {news["description"]}
Original link: {news["url"]}

Important:
- The article must be directly related to the news title and description.
- Do not write generic text.
- Do not mention unrelated topics.
- If the title is about travel plug adaptors, the article must discuss travel plug adaptors, electrical safety, consumer awareness, product risk, and travel preparation.
- Return JSON only.
- No markdown.
- No code block.
- No explanation outside JSON.

Return this exact JSON structure:

{{
  "article": "8 to 12 paragraphs. Original C1-level business/news English learning article. Use paragraph breaks with \\n\\n.",
  "summary": "15 to 20 sentences. Directly summarize the issue and implications in professional English.",
  "vocabulary": [
    {{"word": "word 1", "meaning": "Korean meaning"}},
    {{"word": "word 2", "meaning": "Korean meaning"}},
    {{"word": "word 3", "meaning": "Korean meaning"}},
    {{"word": "word 4", "meaning": "Korean meaning"}},
    {{"word": "word 5", "meaning": "Korean meaning"}},
    {{"word": "word 6", "meaning": "Korean meaning"}},
    {{"word": "word 7", "meaning": "Korean meaning"}},
    {{"word": "word 8", "meaning": "Korean meaning"}}
  ],
  "shadowing": [
    "Sentence 1.",
    "Sentence 2.",
    "Sentence 3.",
    "Sentence 4.",
    "Sentence 5."
  ],
  "quiz": [
    {{
      "question": "Question 1",
      "options": ["A", "B", "C", "D"],
      "answer": "A"
    }},
    {{
      "question": "Question 2",
      "options": ["A", "B", "C", "D"],
      "answer": "B"
    }},
    {{
      "question": "Question 3",
      "options": ["A", "B", "C", "D"],
      "answer": "C"
    }},
    {{
      "question": "Question 4",
      "options": ["A", "B", "C", "D"],
      "answer": "D"
    }},
    {{
      "question": "Question 5",
      "options": ["A", "B", "C", "D"],
      "answer": "A"
    }}
  ]
}}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b:free",
        messages=[
            {
                "role": "system",
                "content": "You create valid JSON only for an English learning web app. Never return markdown."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content
    content = clean_json_text(content)

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        print("AI returned invalid JSON:")
        print(content)
        raise e


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
