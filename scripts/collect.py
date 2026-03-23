#!/usr/bin/env python3
"""
DailyReport - 每日资讯抓取脚本
支持 Tavily API + RSS 订阅源
"""
import json
import os
import re
import requests
from datetime import datetime
from pathlib import Path
from html import unescape

CONFIG = {
    "topics": ["游戏", "AI科技", "股票"],
    "output_dir": "output",
}

# RSS 订阅源列表
RSS_FEEDS = {
    "AI科技": [
        "https://www.36kr.com/information/AI/",
        "https://www.geekpark.com/news",
    ],
    "游戏": [
        "https://www.36kr.com/information/game/",
    ],
    "股票": [
        "https://finance.sina.com.cn/stock/",
    ],
}

def fetch_rss_news(topic):
    """通过网页抓取获取新闻"""
    news = []
    urls = RSS_FEEDS.get(topic, [])
    
    for url in urls:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=10)
            # 简单的标题提取
            titles = re.findall(r'>([^<]{10,50}加速|[^<]{10,50}发布|[^<]{10,50}融资|[^<]{10,50}AI[^<]{0,20})<', resp.text)
            for t in titles[:5]:
                clean_title = unescape(t).strip()
                if clean_title and len(clean_title) > 10:
                    news.append({
                        "title": clean_title,
                        "content": "点击查看详情",
                        "url": url
                    })
        except Exception as e:
            print(f"  ⚠️ 抓取 {url} 失败: {e}")
    
    return news[:5]

def search_news(topic):
    """使用 Tavily API 搜索热点新闻"""
    api_key = os.getenv("TAVILY_API_KEY", "")
    
    if not api_key:
        # 使用 RSS 备用方案
        print(f"  📡 使用 RSS 源: {topic}")
        return fetch_rss_news(topic)
    
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    data = {
        "api_key": api_key,
        "query": f"{topic} 最新消息 2026",
        "search_depth": "basic",
        "max_results": 5
    }
    
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        results = resp.json().get("results", [])
        return [{"title": r.get("title", ""), "content": r.get("content", "")[:200], "url": r.get("url", "")} for r in results]
    except Exception as e:
        print(f"  ⚠️ Tavily 搜索失败: {e}")
        return fetch_rss_news(topic)

def generate_markdown(news_data):
    """生成 Markdown 日报"""
    date = datetime.now().strftime("%Y年%m月%d日")
    
    md = f"""# 📰 每日简报 - {date}

> 关注领域：游戏 · AI科技 · 股票

---
"""
    for topic, articles in news_data.items():
        md += f"\n## 🎯 {topic}\n\n"
        if not articles:
            md += "_暂无内容_\n"
        for i, art in enumerate(articles, 1):
            md += f"{i}. **{art['title']}**\n   - {art['content']}\n   - [原文链接]({art['url']})\n"
    
    md += f"""
---
*由 DailyReport 自动生成 · {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    return md

def generate_html(markdown_content):
    """生成美化版 HTML 页面"""
    date = datetime.now().strftime("%Y年%m月%d日")
    
    # 解析 markdown 提取新闻
    topics_html = ""
    lines = markdown_content.split('\n')
    current_topic = ""
    articles_html = []
    
    for line in lines:
        if line.startswith('## 🎯 '):
            if current_topic and articles_html:
                topics_html += f'''
                <section class="topics-section">
                    <h2 class="section-title">{current_topic}</h2>
                    <div class="topics-grid">
                        {''.join(articles_html)}
                    </div>
                </section>'''
            current_topic = line.replace('## 🎯 ', '')
            articles_html = []
        elif line.strip().startswith('1. **') or line.strip().startswith('2. **') or line.strip().startswith('3. **'):
            match = re.match(r'\d+\. \*\*([^*]+)\*\*', line.strip())
            if match:
                title = match.group(1)
        elif line.strip().startswith('- ') and '原文链接' in line:
            url_match = re.search(r'\(([^)]+)\)', line)
            url = url_match.group(1) if url_match else "#"
            if current_topic and title:
                articles_html.append(f'''
                <div class="topic-card" onclick="window.open('{url}', '_blank')">
                    <div class="topic-icon">📄</div>
                    <div class="topic-name">{title}</div>
                    <div class="topic-desc">点击查看详情 →</div>
                </div>''')
                title = ""
    
    # 闭合最后的 topic
    if current_topic and articles_html:
        topics_html += f'''
        <section class="topics-section">
            <h2 class="section-title">{current_topic}</h2>
            <div class="topics-grid">
                {''.join(articles_html)}
            </div>
        </section>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日简报 | {date}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', sans-serif; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); min-height: 100vh; color: #fff; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 60px 20px; }}
        header {{ text-align: center; margin-bottom: 50px; }}
        .logo {{ font-size: 60px; margin-bottom: 20px; animation: float 3s ease-in-out infinite; }}
        @keyframes float {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-10px); }} }}
        h1 {{ font-size: 42px; font-weight: 700; background: linear-gradient(90deg, #00d9ff, #a855f7, #ff6b6b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 15px; }}
        .subtitle {{ color: rgba(255,255,255,0.6); font-size: 16px; letter-spacing: 2px; }}
        .time-badge {{ display: inline-block; background: rgba(255,255,255,0.1); padding: 8px 20px; border-radius: 30px; margin-top: 20px; font-size: 14px; color: rgba(255,255,255,0.8); border: 1px solid rgba(255,255,255,0.2); }}
        .section-title {{ font-size: 20px; color: rgba(255,255,255,0.9); margin-bottom: 25px; display: flex; align-items: center; gap: 10px; }}
        .section-title::before {{ content: ''; width: 4px; height: 20px; background: linear-gradient(180deg, #00d9ff, #a855f7); border-radius: 2px; }}
        .topics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
        .topic-card {{ background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px; padding: 25px; transition: all 0.3s ease; cursor: pointer; }}
        .topic-card:hover {{ transform: translateY(-5px); background: rgba(255,255,255,0.12); border-color: rgba(255,255,255,0.2); box-shadow: 0 20px 40px rgba(0,0,0,0.3); }}
        .topic-icon {{ font-size: 36px; margin-bottom: 15px; }}
        .topic-name {{ font-size: 16px; font-weight: 600; margin-bottom: 8px; line-height: 1.4; }}
        .topic-desc {{ font-size: 13px; color: rgba(255,255,255,0.5); }}
        footer {{ text-align: center; margin-top: 60px; padding-top: 30px; border-top: 1px solid rgba(255,255,255,0.1); color: rgba(255,255,255,0.4); font-size: 13px; }}
        footer a {{ color: #00d9ff; text-decoration: none; }}
        @media (max-width: 600px) {{ h1 {{ font-size: 28px; }} .container {{ padding: 40px 15px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="logo">📰</div>
            <h1>每日简报</h1>
            <p class="subtitle">DAILY REPORT</p>
            <div class="time-badge">🕐 {date} 自动更新</div>
        </header>
        
        {topics_html}
        
        <footer>
            <p>Powered by <a href="https://github.com/huijiccc/daily-report">GitHub Actions</a></p>
        </footer>
    </div>
</body>
</html>'''
    return html

def main():
    print("🔍 开始收集资讯...")
    
    news_data = {}
    for topic in CONFIG["topics"]:
        print(f"  搜索: {topic}")
        news_data[topic] = search_news(topic)
    
    # 生成 Markdown
    md_content = generate_markdown(news_data)
    output_dir = Path(CONFIG["output_dir"])
    output_dir.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    md_file = output_dir / f"report-{date_str}.md"
    md_file.write_text(md_content, encoding="utf-8")
    print(f"✅ Markdown: {md_file}")
    
    # 生成 HTML
    html_content = generate_html(md_content)
    html_file = output_dir / "index.html"
    html_file.write_text(html_content, encoding="utf-8")
    print(f"✅ HTML: {html_file}")
    
    print("🎉 完成!")

if __name__ == "__main__":
    main()
