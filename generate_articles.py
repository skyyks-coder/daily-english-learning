import json
import datetime
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

TODAY = datetime.datetime.utcnow().date()

DAY_TOPICS = {
    0: {
        "day": "Business",
        "rss": "https://feeds.bbci.co.uk/news/business/rss.xml"
    },
    1: {
        "day": "Travel",
        "rss": "https://feeds.bbci.co.uk/news/world/rss.xml"
    },
    2: {
        "day": "AI",
        "rss": "https://feeds.bbci.co.uk/news/technology/rss.xml"
    },
    3: {
        "day": "Food",
        "rss": "https://feeds.bbci.co.uk/news/world/rss.xml"
    },
    4: {
        "day": "Economy",
        "rss": "https://feeds.bbci.co.uk/news/business/rss.xml"
    },
    5: {
        "day": "Culture",
        "rss": "https://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
    },
    6: {
        "day": "Weekly Review",
        "rss": "https://feeds.bbci.co.uk/news/rss.xml"
    }
}


def fetch_rss(url):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(req, timeout=20) as response:
        xml_data = response.read()

    root = ET.fromstring(xml_data)

    items = root.findall(".//item")

    if not items:
        raise Exception("No RSS items found.")

    item = items[0]

    title = item.findtext("title", default="No title")
    link = item.findtext("link", default="")
    description = item.findtext("description", default="")
    pub_date_raw = item.findtext("pubDate", default="")

    try:
        pub_date = parsedate_to_datetime(pub_date_raw).date().isoformat()
    except Exception:
        pub_date = TODAY.isoformat()

    return {
        "title": title,
        "url": link,
        "description": description,
        "date": pub_date
    }


def generate_c1_summary(title, description, topic):
    summary = f"""
The article discusses a recent development related to {topic.lower()}, highlighting its wider significance for readers who follow global news and business trends.
It presents the issue as part of a broader shift rather than as an isolated event.
The topic is connected to changing economic, technological, social, or cultural conditions.
For English learners, the article offers useful exposure to professional news vocabulary and analytical sentence structures.
The main idea can be understood as a reflection of how institutions, companies, consumers, or governments respond to new pressures.
The development also shows how quickly priorities can change in a connected global environment.
Readers can observe how formal journalism explains causes, consequences, and possible implications.
The language used in this type of article is especially useful for building advanced reading comprehension.
It encourages learners to move beyond basic facts and consider the context behind the news.
The article also provides a good opportunity to practice summarizing information in a concise but sophisticated way.
From a business-English perspective, the topic is relevant because it involves decision-making, risk, strategy, or public response.
Learners can pay attention to verbs that describe change, influence, growth, pressure, and regulation.
They can also notice how news writing often balances factual reporting with cautious interpretation.
The broader significance of the article lies in how it connects present events with longer-term trends.
Overall, the article is suitable for intermediate-to-advanced learners who want to improve their ability to read, speak, and discuss current affairs in English.
""".strip()

    return summary


def generate_learning_article(news, topic):
    article_text = f"""
Title: {news["title"]}

This learning article is based on the linked news item from BBC News.

Original news summary:
{news["description"]}

Learning note:
This article should be read together with the original source link. The text below is not a reproduction of the full copyrighted article. Instead, it is a study-friendly learning version designed for English practice.

The topic is relevant because it reflects current developments in {topic.lower()}. It allows learners to practice reading professional news English while also building vocabulary related to global affairs, business, technology, culture, and public policy. When reading the original article, focus on how the writer introduces the issue, explains the background, and presents the possible consequences. Pay attention to the verbs and linking expressions used to describe change, contrast, and uncertainty.
""".strip()

    return article_text


def build_vocabulary(topic):
    common_words = [
        {
            "word": "development",
            "meaning": "전개, 발전, 새로운 상황"
        },
        {
            "word": "implication",
            "meaning": "영향, 함의"
        },
        {
            "word": "context",
            "meaning": "맥락"
        },
        {
            "word": "strategy",
            "meaning": "전략"
        },
        {
            "word": "shift",
            "meaning": "변화, 전환"
        },
        {
            "word": "response",
            "meaning": "대응, 반응"
        },
        {
            "word": "trend",
            "meaning": "추세"
        }
    ]

    if topic == "AI":
        common_words.extend([
            {
                "word": "automation",
                "meaning": "자동화"
            },
            {
                "word": "algorithm",
                "meaning": "알고리즘"
            },
            {
                "word": "governance",
                "meaning": "관리 체계"
            }
        ])

    if topic == "Economy":
        common_words.extend([
            {
                "word": "inflation",
                "meaning": "인플레이션, 물가 상승"
            },
            {
                "word": "growth",
                "meaning": "성장"
            },
            {
                "word": "consumer demand",
                "meaning": "소비자 수요"
            }
        ])

    if topic == "Business":
        common_words.extend([
            {
                "word": "revenue",
                "meaning": "매출"
            },
            {
                "word": "investment",
                "meaning": "투자"
            },
            {
                "word": "competitive advantage",
                "meaning": "경쟁 우위"
            }
        ])

    return common_words[:8]


def main():
    weekday = datetime.datetime.utcnow().weekday()
    topic_info = DAY_TOPICS[weekday]

    topic = topic_info["day"]
    rss_url = topic_info["rss"]

    news = fetch_rss(rss_url)

    article = {
        "day": topic,
        "title": news["title"],
        "source": "BBC News",
        "date": news["date"],
        "url": news["url"],
        "article": generate_learning_article(news, topic),
        "summary": generate_c1_summary(news["title"], news["description"], topic),
        "vocabulary": build_vocabulary(topic)
    }

    with open("articles.json", "w", encoding="utf-8") as f:
        json.dump([article], f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
