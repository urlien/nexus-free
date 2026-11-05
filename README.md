# Nexus Free - 虚拟角色检索引擎 🔍

**免费开源版** - AI驱动的多源角色搜索 + 角色卡自动生成

> 完全复刻 kcbuy.cn 核心功能 + 大量扩展，全部免费，数据本地存储。

## 📊 项目状态

**当前版本：** v0.9.0 (2026-11-05)
**状态：** 核心管线已重构 + 实战验证通过

| 功能 | 状态 | 说明 |
|------|------|------|
| 20源搜索 | ✅ 完成 | 百科/社区/攻略/创作/通用 |
| AI角色卡生成 | ✅ 完成 | SillyTavern V2 格式 |
| 3D知识图谱 | ✅ 完成 | 力导向可视化 |
| 世界书系统 | ✅ 完成 | 单条目+批量生成 |
| 状态栏系统 | ✅ 完成 | 4种预设 |
| 卡片库 | ✅ 完成 | SQLite本地存储 |
| 长文炼化 | ✅ 完成 | 超长文本分段处理 |
| Docker部署 | ✅ 完成 | 一键启动 |
| 实际测试 | ✅ 通过 | 11-05 用鸣潮素材跑通长文炼化全链路 |

## ✨ 功能

### 🔍 多源角色搜索（20个数据源）

**百科类（11个）**
Fandom · 萌娘百科 · PRTS Wiki · B站BWIKI · AniList · Bangumi · Wikidata · 百度百科 · MyAnimeList · 方舟剧情 · 方舟设定库

**社区类（3个）** 知乎 · NGA · 微博

**攻略类（1个）** GamePress

**分析类（1个）** TV Tropes

**创作类（3个）** Pixiv · Danbooru · AO3

**通用类（1个）** 网页搜索

### 🧠 AI 分析管道
- 角色信息提取 → 结构化数据
- 隐式关系分析 → 暗恋、敌友转化等
- 世界观概念提取 → 货币/食物/语言/宗教/组织
- PLists 描述合成 → 1200-2000字社区标准格式
- 对话示例生成 → SillyTavern mes_example
- 世界书条目生成 → 200-5000字详细条目
- 长文炼化 → 长文本→角色+世界观

### 📝 角色卡系统
- 一键生成：角色名 + 原始文本 → 完整 SillyTavern V2 角色卡
- 多情境开场：5条 alternate_greetings
- 卡片库：SQLite 本地存储，搜索/筛选/CRUD
- 导出：SillyTavern V2 JSON 格式

### 🕸️ 巨型世界书
- 单条目生成：输入概念 → 详细世界书条目
- 自动批量生成：从文本提取所有世界观 → 完整世界书
- **3D 知识图谱**：力导向可视化，节点分类着色，粒子流动
- 世界书管理：创建/查看/删除/条目管理

### 📊 状态栏系统
- 4种预设：空白 / RPG / 服装追踪 / 心理追踪
- 显示格式：table / list / prose
- 刷新模式：every_turn / every_n_turns / on_keyword / on_depth
- 分类字段编辑：图标+名称+字段列表
- AI 生成状态数据
- Prompt 预览
- 复制 JSON / 保存配置

### 📖 长文炼化
- 上传长文本 → 自动提取所有角色 + 世界观
- 分段处理，支持超长文本

## 🛠️ 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3 + FastAPI |
| 前端 | Vue 3 + Tailwind CSS |
| 数据库 | SQLite |
| 图谱 | 3d-force-graph |
| AI | 智谱 GLM-4-Flash（免费）/ Gemini 官方（可切换） |
| 搜索 | 20个数据源公开API |

## 🚀 快速开始

### 方式一：Docker（推荐）

```bash
# 1. 配置 API
 cp .env.example .env
# 编辑 .env 填入 API Key

# 2. 启动
 bash start.sh
# 或直接：
docker compose up -d --build

# 3. 打开浏览器
# http://localhost:8000
```

### 方式二：Python 直接运行

```bash
# 1. 配置 API
cp .env.example .env
# 编辑 .env 填入 API Key

# 2. 安装依赖
cd backend
pip install -r requirements.txt

# 3. 启动
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 4. 打开浏览器
# http://localhost:8000
```

## 📡 API 端点

### 搜索（20源）
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/search?query=名&sources=all` | GET | 多源搜索 |
| `/api/sources` | GET | 数据源列表 |

### AI 生成
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/generate` | POST | 生成角色卡 |
| `/api/extract/relations` | POST | 提取角色关系 |
| `/api/extract/world-concepts` | POST | 提取世界观 |
| `/api/lorebook/entry` | POST | 生成世界书条目 |
| `/api/lorebook/generate` | POST | 批量生成世界书 |
| `/api/long-text` | POST | 长文炼化 |

### 卡片库
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/library/cards` | GET/POST | 列表/创建 |
| `/api/library/cards/{id}` | GET/PUT/DELETE | 详情/更新/删除 |

### 世界书库
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/library/lorebooks` | GET/POST | 列表/创建 |
| `/api/library/lorebooks/{id}` | GET/DELETE | 详情/删除 |
| `/api/library/lorebooks/{id}/entries` | POST | 添加条目 |

### 状态栏
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/status-sheet/presets` | GET | 预设列表 |
| `/api/status-sheet/render` | POST | 渲染状态栏 |
| `/api/status-sheet/preview` | POST | 预览HTML |
| `/api/status-sheet/generate` | POST | AI生成状态 |

### 导出
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/export/card` | POST | 导出 SillyTavern V2 |

## 📋 角色卡输出标准

每个角色输出 3 个文件：

```
[角色名]/
├── 人设-[角色名].txt          ← 8000-10000字
├── [角色名]世界书数据.json      ← 50-170条目
└── [角色名]正则数据.json        ← 状态栏+开场白+正则脚本
```

详见 [OUTPUT-STANDARD.md](OUTPUT-STANDARD.md)

## 📝 更新日志

### v0.9.0 (2026-11-05)
- 🔥 **长文炼化管线彻底重写**：废掉"只处理前 5 段"的硬截断
- ✅ **三步管线**：全局识人（扫角色名单 + 别名）→ 定向提取（按 major 角色聚合上下文）→ 去重合并
- ✅ **LLM 层支持双 provider**：智谱 GLM-4-Flash（免费国内直连）/ Gemini 官方（代理）
- ✅ **强制锁死角色名**：防止 LLM 因上下文串味而改错主角
- ✅ **关系过滤**：剔除"心声·二"这类非人名噪音
- ✅ **实战验证**：从 4588 字鸣潮混杂文本中正确提取散华、今汐、漂泊者三个角色档案
- ✅ 503 自动重试、JSON 强约束、markdown 代码块清洗

### v0.8.0 (2026-07-31)
- ✅ Docker部署（Dockerfile + docker-compose.yml）
- ✅ 一键启动脚本（start.sh，自动检测Docker/Python）
- ✅ .env.example 配置模板
- ✅ .gitignore 排除敏感文件
- ✅ 工作日志文档

### v0.7.0 (2026-07-14)
- ✅ 角色卡输出标准文档
- ✅ 参考文件（蕾缪安+黍的人设/世界书/正则）

### v0.6.0 (2026-07-14)
- ✅ 明日方舟专用数据源：方舟剧情+方舟设定库
- ✅ 数据源总数: 20个

### v0.5.0 (2026-07-13)
- ✅ 前端完全复刻 kcbuy.cn Tailwind 风格
- ✅ 新增 10 个数据源
- ✅ 3D 知识图谱
- ✅ 巨型世界书+长文炼化 Tab
- ✅ 设置页/状态栏/卡片库完整功能

### v0.4.0 (2026-07-13)
- ✅ 卡片库系统（SQLite）
- ✅ 状态栏系统（4种预设）
- ✅ 完整前端（5个Tab）

### v0.3.0 (2026-07-13)
- ✅ 8个搜索源全部完成
- ✅ 世界书条目生成+长文炼化

### v0.2.0 (2026-07-13)
- ✅ MiMo API 接入
- ✅ AI 角色分析管道
- ✅ SillyTavern V2 导出

### v0.1.0 (2026-06-29)
- ✅ 项目初始化
- ✅ FastAPI + Vue 3 基础框架

## 📄 License

MIT
