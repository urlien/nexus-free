# Nexus Free - 虚拟角色检索引擎 🔍

**免费开源版** - AI驱动的多源角色搜索 + 角色卡自动生成

> 完全复刻 kcbuy.cn 核心功能，全部免费，数据本地存储。

## ✨ 功能全景

### 🔍 多源角色搜索（18个数据源）
**百科类（9个）**：Fandom · 萌娘百科 · PRTS Wiki · B站BWIKI · AniList · Bangumi · Wikidata · 百度百科 · MyAnimeList
**社区类（3个）**：知乎 · NGA · 微博
**攻略类（1个）**：GamePress
**分析类（1个）**：TV Tropes
**创作类（3个）**：Pixiv · Danbooru · AO3
**通用类（1个）**：网页搜索

### 🧠 AI 分析管道（MiMo / DeepSeek / 任意OpenAI兼容API）
- 角色信息提取 → 结构化数据
- 隐式关系分析 → 暗恋、敌友转化等
- 世界观概念提取 → 货币/食物/语言/宗教/组织
- PLists 描述合成 → 1200-2000字社区标准格式
- 对话示例生成 → SillyTavern mes_example
- 世界书条目生成 → 200-5000字详细条目

### 📝 角色卡系统
- 一键生成：角色名 + 原始文本 → 完整 SillyTavern V2 角色卡
- 多情境开场：5条 alternate_greetings
- 卡片库：SQLite 本地存储，搜索/筛选/CRUD
- 导出：SillyTavern V2 JSON 格式

### 🕸️ 世界书系统
- 单条目生成：输入概念 → 详细世界书条目
- 自动批量生成：从文本提取所有世界观 → 完整世界书
- 世界书管理：创建/查看/删除/条目管理

### 📊 状态栏系统
- 4种预设：默认 / RPG / 视觉小说 / 简约
- AI 生成角色状态数据
- HTML/纯文本双格式渲染
- 实时预览

### 📖 长文炼化
- 上传长文本 → 自动提取所有角色 + 世界观
- 分段处理，支持超长文本

## 🛠️ 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3 + FastAPI |
| 前端 | Vue 3 (CDN) |
| 数据库 | SQLite |
| AI | MiMo v2.5 / DeepSeek (OpenAI兼容) |
| 搜索 | 8个 Wiki/数据库公开API |

## 🚀 快速开始

```bash
# 1. 配置API
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

## 📡 完整 API 端点

### 搜索
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

## 📝 更新日志

### v0.4.0 (2026-07-13) - 完整功能版
- ✅ 卡片库系统：SQLite 本地存储 + CRUD + 搜索筛选
- ✅ 世界书系统：创建/管理/条目添加
- ✅ 状态栏系统：4种预设 + AI生成 + 渲染预览
- ✅ 完整前端：搜索/卡片库/世界书/状态栏/AI生成 五大模块
- ✅ 长文炼化端点

### v0.3.0 (2026-07-13)
- ✅ 8个搜索源全部完成
- ✅ 世界书条目生成
- ✅ 长文炼化

### v0.2.0 (2026-07-13)
- ✅ MiMo API 接入
- ✅ AI 角色分析管道
- ✅ SillyTavern V2 导出

### v0.1.0 (2026-06-29)
- ✅ 项目初始化
- ✅ FastAPI + Vue 3 基础框架

## 📄 License

MIT
