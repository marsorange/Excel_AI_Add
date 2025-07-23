# Excel AI 助手 - 设置指南

## 项目概述
Excel AI 助手是一个基于人工智能的Excel插件，提供智能公式生成、公式解释和AI对话功能。

## 技术栈
- **前端**: React + TypeScript + Fluent UI
- **后端**: FastAPI + SQLAlchemy + Python
- **AI模型**: DeepSeek API
- **数据库**: SQLite (默认) / PostgreSQL (可选)

## 环境要求
- Node.js >= 16.0
- Python >= 3.8
- Excel 2021 或 Microsoft 365

## 安装与配置

### 1. 克隆项目
```bash
git clone [项目地址]
cd Excel_AI
```

### 2. 后端配置

#### 安装Python依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 配置环境变量
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置以下配置：
# DEEPSEEK_API_KEY=你的DeepSeek API密钥
# SECRET_KEY=你的JWT密钥
```

#### 获取 DeepSeek API Key
1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册并创建API密钥
3. 将密钥填入 `.env` 文件中的 `DEEPSEEK_API_KEY`

#### 初始化数据库
```bash
# 创建数据库表
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"
```

### 3. 前端配置

#### 安装Node.js依赖
```bash
# 回到项目根目录
cd ..
npm install
```

#### 开发证书（Excel插件需要）
```bash
# Excel插件需要HTTPS证书
npx office-addin-dev-certs install
```

## 运行项目 🚀

### 🎯 两种运行模式

#### 模式1：Excel插件开发 (HTTPS)
```bash
# 后端
cd backend && uvicorn main:app --reload

# 前端 (HTTPS模式)
npm run dev-server
```
- 访问：https://localhost:3000
- 用于Excel插件开发和调试
- 需要安装开发证书

#### 模式2：浏览器测试 (HTTP) ⭐推荐用于测试
```bash
# 后端
cd backend && uvicorn main:app --reload

# 前端 (HTTP模式)
npm run browser-test
```
- 访问：http://localhost:3000
- 便于浏览器直接测试
- 无需证书，避免HTTPS证书问题

### 方法一：使用自动化脚本
```bash
python check_and_start.py
```

## 测试和验证

### 🌐 浏览器测试
1. 启动浏览器测试模式：`npm run browser-test`
2. 打开测试页面：`browser-test.html`
3. 或直接访问：http://localhost:3000

### 📊 Excel插件测试
1. 启动HTTPS模式：`npm run dev-server`
2. 打开Excel
3. 加载插件：`插入` > `Office 加载项` > `上传我的加载项` > 选择 `manifest.xml`

### 🔍 连接测试
```bash
# 测试后端API
curl http://localhost:8000/api/llm-info

# 验证清单文件
npm run validate
```

## API端点
- **浏览器测试**: http://localhost:3000 ⭐便于测试
- **Excel插件**: https://localhost:3000 (需证书)
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

## 主要功能
1. **用户认证**: 注册/登录系统
2. **公式生成**: 自然语言转Excel公式
3. **公式解释**: 解释复杂Excel公式含义
4. **AI助手**: 智能对话和Excel操作建议

## 故障排除

### 常见问题
1. **端口冲突**: 确保3000和8000端口未被占用
2. **证书问题**: Excel插件需要HTTPS证书，浏览器测试使用HTTP
3. **API连接失败**: 检查后端是否正常启动
4. **DeepSeek API错误**: 验证API密钥是否正确配置

### 访问模式选择
- **开发Excel插件**: 使用 `npm run dev-server` (HTTPS)
- **浏览器功能测试**: 使用 `npm run browser-test` (HTTP) 👍推荐
- **生产环境**: 全部使用HTTPS

### 日志查看
- 前端日志：浏览器开发者工具Console
- 后端日志：终端输出
- Excel插件日志：Excel开发者工具

### NPM脚本说明
```bash
npm run dev-server        # HTTPS模式，用于Excel插件
npm run browser-test       # HTTP模式，用于浏览器测试
npm run dev-server-http    # HTTP模式（别名）
npm run validate          # 验证manifest.xml
npm run start             # 启动Excel调试
```

## 部署
参考 `PROJECT_STATUS.md` 中的部署指南进行生产环境部署。

---

**💡 小贴士**: 
- 初次测试推荐使用**浏览器HTTP模式**，避免证书配置问题
- Excel插件开发时使用**HTTPS模式**确保兼容性
- 使用 `browser-test.html` 快速测试所有功能