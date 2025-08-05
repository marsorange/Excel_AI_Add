# Excel AI 助手 - 安装配置指南

## 项目概述

Excel AI 助手是一个基于 Office Add-in 的智能 Excel 助手，提供以下功能：

- **AI模型**: Qwen API
- **Excel操作**: 读取数据、生成公式、创建图表
- **智能对话**: 自然语言交互
- **实时响应**: 即时反馈和操作

## 环境要求

- Python 3.8+
- Node.js 16+
- Office 365 或 Excel 2016+
- 有效的 Qwen API Key

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd Excel_AI
```

### 2. 安装依赖

#### 后端依赖
```bash
cd backend
pip install -r requirements.txt
```

#### 前端依赖
```bash
npm install
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=sqlite:///./excel_ai.db

# Qwen API配置
DASHSCOPE_API_KEY=你的Qwen API密钥



# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

#### 获取 Qwen API Key

1. 访问 [阿里云 DashScope](https://dashscope.aliyun.com/)
2. 注册账号并获取 API Key
3. 将密钥填入 `.env` 文件中的 `DASHSCOPE_API_KEY`

### 4. 初始化数据库

```bash
cd backend
alembic upgrade head
```

### 5. 启动服务

#### 启动后端服务
```bash
cd backend
python main.py
```

#### 启动前端开发服务器
```bash
npm run dev
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `QWEN_API_KEY` | Qwen API 密钥 | 是 |
| `OPENAI_API_KEY` | OpenAI API 密钥（备用） | 否 |
| `DATABASE_URL` | 数据库连接字符串 | 是 |
| `HOST` | 服务器主机 | 否 |
| `PORT` | 服务器端口 | 否 |
| `DEBUG` | 调试模式 | 否 |

### API 配置

项目支持两种 AI 模型配置：

1. **Qwen API**（推荐）：阿里云通义千问模型



## 故障排除

### 常见问题

1. **依赖安装失败**: 确保 Python 和 Node.js 版本符合要求
2. **数据库连接错误**: 检查 DATABASE_URL 配置
3. **Qwen API错误**: 验证API密钥是否正确配置
4. **端口占用**: 修改 PORT 环境变量或关闭占用端口的程序

### 调试模式

设置 `DEBUG=true` 启用详细日志输出：

```bash
export DEBUG=true
python main.py
```

## 开发指南

### 项目结构

```
Excel_AI/
├── backend/          # 后端服务
│   ├── main.py      # 主程序
│   ├── models.py    # 数据模型
│   ├── crud.py      # 数据库操作
│   └── llm_config.py # LLM配置
├── src/             # 前端代码
│   ├── taskpane/    # Office Add-in
│   └── commands/    # 命令模块
├── assets/          # 静态资源
└── docs/           # 文档
```

### 添加新功能

1. 在 `backend/` 中添加后端逻辑
2. 在 `src/taskpane/` 中添加前端组件
3. 更新 API 文档和测试用例

## 许可证

本项目采用 MIT 许可证。