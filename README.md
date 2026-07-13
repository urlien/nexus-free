# Nexus Free - 虚拟角色检索引擎 🔍

**免费开源版** - AI驱动的多源角色搜索 + 角色卡自动生成

> 复刻 kcbuy.cn 的核心功能，完全免费，数据本地存储。

## ✨ 功能

### 已完成 ✅
- 🔍 **多源角色搜索** - Fandom、萌娘百科（已实现）
- 🧠 **AI分析管道** - MiMo API 集成，角色信息提取/关系分析/世界观提取
- 📝 **角色卡生成** - 自动生成 SillyTavern V2 标准格式
- 📊 **SillyTavern V2 导出** - 完整字段导出

### 开发中 🚧
- 🕸️ **巨型世界书** - AI自动构建完整世界观
- 📖 **长文炼化** - 上传TXT/PDF自动生成角色卡
- 📚 **卡片库** - 本地管理角色卡收藏
- 📊 **状态栏** - 按标准格式生成状态栏
- 🔍 **更多数据源** - PRTS、BWIKI、AniList、Bangumi

## 🛠️ 技术栈

- **后端**: Python + FastAPI
- **前端**: Vue 3
- **AI**: MiMo v2.5（可配置任意OpenAI兼容API）
- **搜索**: 各wiki公开API（免费）

## 🚀 快速开始

```bash
# 1. 配置API
cp .env.example .env
# 编辑 .env 填入你的 MiMo API Key

# 2. 后端
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload

# 3. 前端（开发模式）
cd frontend
# 直接用浏览器打开 index.html 即可
```

## 📡 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/search?query=角色名` | GET | 搜索角色 |
| `/api/generate` | POST | AI生成角色信息 |
| `/api/extract/relations` | POST | 提取角色关系 |
| `/api/extract/world-concepts` | POST | 提取世界观概念 |
| `/api/export/card` | POST | 导出角色卡 |

## 📝 更新日志

### v0.2.0 (2026-07-13)
- ✅ 接入 MiMo API (mimo-flash)
- ✅ 实现 AI 角色信息提取管道
- ✅ 实现角色关系分析
- ✅ 实现世界观概念提取
- ✅ 实现完整角色卡生成流程
- ✅ SillyTavern V2 格式导出

### v0.1.0 (2026-06-29)
- ✅ 项目初始化
- ✅ FastAPI 后端框架
- ✅ Fandom/萌娘百科搜索
- ✅ Vue 3 前端搜索界面

## 📄 License

MIT
