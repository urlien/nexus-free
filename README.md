# Nexus Free - 虚拟角色检索引擎 🔍

**免费开源版** - AI驱动的多源角色搜索 + 角色卡自动生成

> 复刻 kcbuy.cn 的核心功能，完全免费，数据本地存储。

## ✨ 功能

### 🔍 多源角色搜索（8个数据源）
| 数据源 | 说明 | 状态 |
|--------|------|------|
| Fandom Wiki | 全球最大Wiki平台 | ✅ |
| 萌娘百科 | 中文二次元百科 | ✅ |
| PRTS Wiki | 明日方舟专用 | ✅ |
| B站BWIKI | 国产手游数据 | ✅ |
| AniList | 50万+动漫角色 | ✅ |
| Bangumi | 中文ACGN数据库 | ✅ |
| Wikidata | 跨平台ID映射 | ✅ |
| 网页搜索 | 通用兜底方案 | ✅ |

### 🧠 AI分析管道
- **角色信息提取** - 从任意文本提取结构化角色数据
- **关系分析** - 发现隐式角色关系（暗恋、敌友转化等）
- **世界观提取** - 自动识别货币、食物、语言、宗教、组织等
- **描述合成** - 生成1200-2000字PLists格式描述
- **对话生成** - SillyTavern格式对话示例

### 📝 角色卡生成
- **一键生成** - 输入角色名+原始文本 → 完整角色卡
- **SillyTavern V2 格式** - 标准导出，直接导入使用
- **多情境开场** - 5条不同场景的alternate_greetings

### 🕸️ 世界书系统
- **单条目生成** - 输入概念 → 详细世界书条目
- **自动生成** - 从文本批量提取世界观 → 完整世界书
- **SillyTavern Lorebook 格式** - 直接导入

### 📖 长文炼化
- **TXT/长文本 → 角色信息 + 世界观** - 自动分段处理
- **多角色识别** - 从长文本中提取所有角色

### 📚 卡片库 & 状态栏
- 卡片库（开发中）
- 状态栏生成（开发中）

## 🛠️ 技术栈

- **后端**: Python + FastAPI
- **前端**: Vue 3
- **AI**: MiMo v2.5 / DeepSeek（可配置任意OpenAI兼容API）
- **搜索**: 各wiki公开API（免费）

## 🚀 快速开始

```bash
# 1. 配置API
cp .env.example .env
# 编辑 .env 填入你的 API Key

# 2. 后端
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload

# 3. 打开前端
# 浏览器打开 frontend/index.html
```

## 📡 API 端点

### 搜索
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/search?query=角色名` | GET | 多源搜索 |
| `/api/search?query=角色名&sources=prts,bwiki` | GET | 指定数据源 |
| `/api/sources` | GET | 列出所有数据源 |

### AI 生成
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/generate` | POST | AI生成角色卡 |
| `/api/extract/relations` | POST | 提取角色关系 |
| `/api/extract/world-concepts` | POST | 提取世界观概念 |

### 世界书
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/lorebook/entry` | POST | 生成单个条目 |
| `/api/lorebook/generate` | POST | 自动生成完整世界书 |

### 长文炼化
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/long-text` | POST | 长文本→角色+世界观 |

### 导出
| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/export/card` | POST | 导出SillyTavern V2角色卡 |

## 📝 更新日志

### v0.3.0 (2026-07-13)
- ✅ 新增6个搜索源：PRTS、BWIKI、AniList、Bangumi、Wikidata、网页搜索
- ✅ 世界书系统：单条目生成 + 自动批量生成
- ✅ 长文炼化：TXT/长文本 → 角色信息 + 世界观
- ✅ API /sources 端点

### v0.2.0 (2026-07-13)
- ✅ 接入 MiMo API (mimo-flash)
- ✅ AI角色信息提取管道
- ✅ 角色关系分析
- ✅ 世界观概念提取
- ✅ 完整角色卡生成流程
- ✅ SillyTavern V2 格式导出

### v0.1.0 (2026-06-29)
- ✅ 项目初始化
- ✅ FastAPI 后端框架
- ✅ Fandom/萌娘百科搜索
- ✅ Vue 3 前端搜索界面

## 📄 License

MIT
