# 环境变量配置
# 复制此文件并重命名为 .env，然后修改相应的值

DATABASE_URL = "sqlite:///./sql_app.db"
SECRET_KEY = "your-secret-key-here-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# DeepSeek API 配置
DEEPSEEK_API_KEY = "你的API_KEY"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions" 