# 📰 DailyReport

每日自动生成的资讯简报，部署在 GitHub Pages。

## 🎯 关注领域

- 🎮 游戏
- 🤖 AI科技
- 📈 股票

## 🛠️ 技术架构

- 定时任务：GitHub Actions
- 信息抓取：Tavily API / Web搜索
- 站点生成：静态HTML
- 托管：GitHub Pages

## 🚀 手动部署

```bash
# 1. 安装依赖
pip install requests pyyaml

# 2. 运行收集脚本
python scripts/collect.py

# 3. 推送到 GitHub
git add .
git commit -m "Update report"
git push
```

## ⚙️ 配置

修改 `config.yaml` 更改关注领域和搜索参数。

## 📄 许可证

MIT
