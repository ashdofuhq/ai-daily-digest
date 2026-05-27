# AI Daily Digest — 每日 AI 热点

每天自动收集 AI 领域最热门的论文、开源项目、社区讨论，汇总展示在精美的前端网站中。

## 数据来源

- **Arxiv** — cs.AI / cs.LG / cs.CL / cs.CV 最新论文
- **GitHub Trending** — AI/ML 相关热门仓库
- **HuggingFace** — Daily Papers 社区精选
- **Papers With Code** — Trending papers
- **Hacker News** — AI 关键词热门讨论

## 项目结构

```
ai-daily-digest/
├── collector/          # Python 数据采集模块
│   ├── main.py        # 采集入口
│   ├── sources/       # 各数据源适配器
│   ├── dedup.py       # 去重 + 热度评分
│   └── requirements.txt
├── data/              # 采集 JSON 数据
├── web/               # 前端静态站点
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js
├── run.bat            # Windows 定时任务脚本
└── .github/workflows/ # GitHub Actions
```

## 本地运行

### 1. 运行数据采集

```bash
python collector/main.py
```

采集结果会写入 `data/latest.json`、`data/{date}.json` 和 `data/archive.json`。

### 2. 预览前端

用任意 HTTP 服务器打开 `web/` 目录：

```bash
cd web
python -m http.server 8080
```

然后访问 `http://localhost:8080`。

## 定时任务配置 (Windows)

1. 编辑 `run.bat`，确认 Python 路径和项目路径正确
2. 打开 **任务计划程序** (Task Scheduler)
3. 创建基本任务：
   - 名称：`AI Daily Digest`
   - 触发器：**每天**，时间设为 **08:00**
   - 操作：**启动程序** → 选择 `run.bat`
   - 条件：勾选"仅在接通电源时运行"

## 部署到 GitHub Pages

1. 在 GitHub 创建仓库
2. 推送代码到 `main` 分支
3. Settings → Pages → Source: `main` 分支，目录 `/web`
4. 访问 `https://<username>.github.io/<repo>/`

## 技术栈

- 纯 Python 标准库（无需 pip install）
- 纯 HTML/CSS/JS（零前端依赖）
- GitHub Pages 免费托管
