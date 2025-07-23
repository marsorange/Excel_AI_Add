# DeepSeek API 配置指南

## 问题描述
当前项目出现以下错误：
```
DeepSeek API returned an error: {"error":{"message":"Authentication Fails, Your api key: ****here is invalid","type":"authentication_error","param":null,"code":"invalid_request_error"}}
```

这是因为DeepSeek API Key没有正确配置导致的认证失败。

## 解决方案

### 1. 获取DeepSeek API Key

1. 访问 [DeepSeek Platform](https://platform.deepseek.com/)
2. 注册账号并登录
3. 进入控制台，找到 "API Keys" 或"密钥管理"
4. 创建新的API Key（通常以`sk-`开头）
5. 复制生成的API Key（注意：只显示一次，请妥善保存）

### 2. 配置环境变量

在 `backend/` 目录下创建 `.env` 文件（如果不存在），内容如下：

```env
# 数据库配置
DATABASE_URL="sqlite:///./sql_app.db"

# JWT 认证配置  
SECRET_KEY="your-secret-key-here-change-this-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# DeepSeek API 配置
# 将下面的占位符替换为您的真实API Key
DEEPSEEK_API_KEY="sk-5b1fb7eac8754b85ba54e45e11859d69"
DEEPSEEK_API_URL="https://api.deepseek.com/v1/chat/completions"

# 开发环境配置
NODE_ENV="development"
DEBUG=True
```

### 3. 验证配置

创建`.env`文件后：
1. 重启后端服务
2. 测试API调用
3. 检查控制台是否还有认证错误

### 4. 备用方案

如果环境变量方式不可行，可以直接在`main.py`中临时设置：

```python
# 在 main.py 第32行附近，临时替换为：
DEEPSEEK_API_KEY = "sk-your-actual-api-key-here"  # 替换为真实的API Key
```

**注意**: 这种方式仅用于测试，生产环境请使用环境变量。

### 5. 安全提醒

- 不要将真实的API Key提交到代码仓库
- 使用`.gitignore`确保`.env`文件不被版本控制
- 定期轮换API Key
- 监控API使用情况和费用

### 6. 故障排查

如果仍有问题，请检查：
1. API Key格式是否正确（通常以`sk-`开头）
2. API Key是否已激活
3. 账户是否有足够余额
4. 网络连接是否正常
5. API URL是否正确 