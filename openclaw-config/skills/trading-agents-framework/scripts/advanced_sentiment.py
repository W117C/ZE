#!/usr/bin/env python3
"""
Advanced Sentiment Analyzer: NLP-level sentiment scoring, topic clustering, and intensity calculation.

Features:
- Keyword-based sentiment with weighted scoring
- Topic clustering (group posts by topic)
- Sentiment intensity calculation (0-100 scale)
- Sentiment trend tracking over time

Usage:
  python3 advanced_sentiment.py --posts ./reddit_posts.json
  python3 advanced_sentiment.py --symbol 600519
"""
import argparse, json, re, collections, statistics, time
from pathlib import Path

# Extended sentiment lexicon with weights
POS_LEXICON = {
    'buy': 2, 'bull': 2, 'long': 1, 'beat': 2, 'growth': 2, 'strong': 1,
    'undervalued': 2, 'moon': 3, 'up': 1, 'rally': 2, 'breakout': 2,
    'catalyst': 1, 'upgrade': 2, 'outperform': 2, 'recommend': 1,
    'opportunity': 1, 'potential': 1, 'promising': 2, 'excellent': 2,
    'impressive': 2, 'momentum': 1, 'surge': 2, 'soar': 3
}

NEG_LEXICON = {
    'sell': 2, 'bear': 2, 'short': 1, 'miss': 2, 'weak': 1,
    'overvalued': 2, 'down': 1, 'risk': 1, 'drop': 2, 'crash': 3,
    'downgrade': 2, 'underperform': 2, 'avoid': 2, 'danger': 2,
    'bubble': 2, 'correction': 1, 'decline': 1, 'plunge': 3,
    'concern': 1, 'warning': 1, 'loss': 2, 'bankruptcy': 3
}

# Topic keywords for clustering
TOPIC_KEYWORDS = {
    'earnings': ['earnings', 'revenue', 'profit', 'eps', 'quarter', 'report', 'beat', 'miss'],
    'valuation': ['pe', 'pb', 'valuation', 'expensive', 'cheap', 'undervalued', 'overvalued'],
    'technical': ['trend', 'support', 'resistance', 'breakout', 'breakdown', 'ma', 'rsi', 'macd'],
    'news': ['news', 'announcement', 'sec', 'filing', 'lawsuit', 'regulation'],
    'sentiment': ['hype', 'fomo', 'fear', 'greed', 'crowded', 'momentum'],
    'product': ['product', 'launch', 'innovation', 'ai', 'technology', 'platform'],
    'competition': ['competitor', 'market share', 'dominant', 'threat', 'disruption'],
    'macro': ['rate', 'inflation', 'fed', 'recession', 'gdp', 'employment']
}

STOP = set(['the', 'and', 'for', 'with', 'that', 'this', 'from', 'have', 'will', 'just',
            'about', 'your', 'into', 'more', 'than', 'stock', 'is', 'it', 'to', 'of',
            'in', 'a', 'an', 'on', 'at', 'by', 'as', 'are', 'was', 'were', 'be', 'been'])


def tokenize(text):
    return [w.lower() for w in re.findall(r'[A-Za-z]{2,}', text) if w.lower() not in STOP]


def score_post(text):
    """给单个帖子打情绪分（-100 到 +100）"""
    tokens = tokenize(text)
    pos_score = sum(POS_LEXICON.get(t, 0) for t in tokens)
    neg_score = sum(NEG_LEXICON.get(t, 0) for t in tokens)
    raw = pos_score - neg_score
    # Normalize to -100 ~ +100
    intensity = min(100, max(-100, raw * 10))
    return intensity


def classify_topics(posts):
    """主题聚类：按话题分组帖子"""
    clusters = {topic: [] for topic in TOPIC_KEYWORDS}
    for post in posts:
        text = f"{post.get('title', '')} {post.get('text', '')}".lower()
        tokens = set(tokenize(text))
        for topic, keywords in TOPIC_KEYWORDS.items():
            if any(k in tokens for k in keywords):
                clusters[topic].append(post)
    # Remove empty clusters
    return {k: v for k, v in clusters.items() if v}


def analyze_sentiment(posts):
    """高级情绪分析"""
    if not posts:
        return {
            'overall_sentiment': 'neutral',
            'sentiment_score': 0,
            'sentiment_intensity': 0,
            'post_count': 0,
            'topic_clusters': {},
            'top_keywords': [],
            'consensus': 'N/A',
            'confidence': 'low'
        }

    scores = []
    topics = []
    bag = collections.Counter()

    for post in posts:
        text = f"{post.get('title', '')} {post.get('selftext', '')}"
        score = score_post(text)
        scores.append(score)
        bag.update(tokenize(text))

    # Overall metrics
    mean_score = statistics.mean(scores) if scores else 0
    median_score = statistics.median(scores) if scores else 0
    std_score = statistics.stdev(scores) if len(scores) > 1 else 0

    # Intensity: how far from neutral
    intensity = abs(mean_score)

    # Sentiment category
    if mean_score > 20:
        overall = 'bullish'
    elif mean_score > 5:
        overall = 'slightly_bullish'
    elif mean_score < -20:
        overall = 'bearish'
    elif mean_score < -5:
        overall = 'slightly_bearish'
    else:
        overall = 'neutral'

    # Topic clustering
    clusters = classify_topics(posts)
    cluster_summary = {
        topic: {
            'count': len(posts_in_topic),
            'avg_sentiment': round(statistics.mean([score_post(f"{p.get('title','')} {p.get('selftext','')}") for p in posts_in_topic]), 1)
        }
        for topic, posts_in_topic in clusters.items()
    }

    # Top keywords
    top_keywords = [w for w, _ in bag.most_common(10)]

    # Consensus: how aligned are posts
    consensus = 'high' if std_score < 15 else 'medium' if std_score < 30 else 'low'

    return {
        'overall_sentiment': overall,
        'sentiment_score': round(mean_score, 1),
        'sentiment_median': round(median_score, 1),
        'sentiment_intensity': round(intensity, 1),
        'std_deviation': round(std_score, 1),
        'consensus': consensus,
        'post_count': len(posts),
        'topic_clusters': cluster_summary,
        'top_keywords': top_keywords,
        'confidence': 'high' if len(posts) >= 10 else 'medium' if len(posts) >= 3 else 'low'
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--posts')
    p.add_argument('--symbol')
    p.add_argument('--json', action='store_true')
    args = p.parse_args()

    if args.posts:
        posts = json.loads(Path(args.posts).read_text())
    elif args.symbol:
        # Try to get from Reddit cache
        cache_path = Path.home()/'.openclaw'/'skills'/'trading-agents-framework'/'assets.reddit_cache.sqlite3'
        if cache_path.exists():
            import sqlite3
            conn = sqlite3.connect(cache_path)
            row = conn.execute('SELECT payload FROM reddit_cache WHERE symbol=?', (args.symbol,)).fetchone()
            if row:
                data = json.loads(row[0])
                posts = data.get('posts', [])
            else:
                posts = []
        else:
            posts = []
    else:
        print("Error: provide --posts or --symbol", file=sys.stderr)
        sys.exit(1)

    result = analyze_sentiment(posts)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("=== Advanced Sentiment Analysis ===")
        print(f"总体情绪: {result['overall_sentiment']}")
        print(f"情绪分数: {result['sentiment_score']}")
        print(f"情绪强度: {result['sentiment_intensity']}")
        print(f"共识度: {result['consensus']}")
        print(f"帖子数: {result['post_count']}")
        print(f"\n主题分布:")
        for topic, info in result['topic_clusters'].items():
            print(f"  {topic}: {info['count']} 帖, 平均情绪 {info['avg_sentiment']}")
        print(f"\nTop 关键词: {', '.join(result['top_keywords'][:5])}")
        print("=== End ===")


if __name__ == '__main__':
    main()
