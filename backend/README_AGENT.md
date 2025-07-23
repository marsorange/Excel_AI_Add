# Excel 智能 Agent 后端集成说明

## 🎯 功能概述

本项目已成功集成 langGraph 框架，实现了基础的对话 Agent 功能，能够：

1. **理解自然语言指令** - 解析用户的 Excel 操作需求
2. **自动规划操作步骤** - 基于意图选择合适的工具组合
3. **生成 Excel API 调用** - 输出可在前端执行的 Office.js 代码
4. **多步推理与反思** - 支持复杂任务的自动拆解和执行

## 📁 新增文件结构

```
backend/
├── excel_tools.py          # Excel API 工具集封装
├── agent_core.py           # langGraph Agent 核心逻辑  
├── test_agent.py           # Agent 功能测试脚本
├── README_AGENT.md         # 本说明文档
└── schemas.py              # 新增 Agent 相关数据模型
```

## 🔧 已实现的功能

### 1. Excel API 工具集 (`excel_tools.py`)

- **ReadRangeTool** - 读取单元格范围数据
- **WriteRangeTool** - 写入单元格数据
- **FormulaGeneratorTool** - 生成 Excel 公式
- **CreateChartTool** - 创建图表

### 2. Agent 核心 (`agent_core.py`)

- **意图理解** - 分析用户自然语言请求
- **工具选择** - 自动选择合适的 Excel 操作工具
- **代码生成** - 生成可执行的 Office.js 代码片段
- **响应生成** - 生成友好的中文回复

### 3. API 接口 (`main.py`)

新增 `/agent/chat` 端点：

```python
POST /agent/chat
{
    "message": "请帮我统计A列的总和",
    "conversation_id": "optional",
    "context": {}
}
```

响应格式：
```python
{
    "success": true,
    "response": "我已经为您生成了求和公式...",
    "excel_operations": [
        {
            "operation_type": "generate_formula",
            "description": "生成求和公式", 
            "js_code": "Excel.run(async (context) => { ... });",
            "parameters": {...}
        }
    ],
    "conversation_id": "demo_conversation_001"
}
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 运行测试

```bash
python test_agent.py
```

预期输出：
```
🎉 所有测试通过！Agent 基础框架已就绪。
```

### 3. 启动服务

```bash
uvicorn main:app --reload --port 8000
```

### 4. 测试 API（需要先注册/登录获取 token）

```bash
curl -X POST "http://localhost:8000/agent/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "请帮我计算销售数据的平均值"
  }'
```

## 🔑 启用完整 Agent 功能

目前为演示版本，要启用完整的 AI 功能，需要：

### 1. 配置 OpenAI API Key

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

或在 `.env` 文件中：
```
OPENAI_API_KEY=your-openai-api-key
```

### 2. 修改 Agent 初始化（可选）

在 `main.py` 中集成完整的 Agent：

```python
from agent_core import get_agent

@app.post("/agent/chat")
async def agent_chat(request: schemas.AgentChatRequest, ...):
    try:
        agent = get_agent(api_key=os.getenv("OPENAI_API_KEY"))
        result = await agent.process_request(request.message)
        return schemas.AgentChatResponse(**result)
    except Exception as e:
        # 错误处理
```

## 🔍 工具扩展示例

添加新的 Excel 工具：

```python
# excel_tools.py
class FilterDataTool(BaseTool):
    name = "filter_data"
    description = "筛选和过滤 Excel 数据"
    
    def _run(self, criteria: str, range_address: str = "A1:Z1000") -> str:
        # 实现筛选逻辑
        js_code = f"""
        Excel.run(async (context) => {{
            const sheet = context.workbook.worksheets.getActiveWorksheet();
            const range = sheet.getRange("{range_address}");
            // 添加筛选逻辑
            await context.sync();
        }});
        """
        return json.dumps({"js_code": js_code, "success": True})
```

## 🎯 前端集成建议

### 1. 在 React 组件中调用 Agent

```typescript
// src/taskpane/components/AgentChat.tsx
const callAgent = async (message: string) => {
  const response = await fetch('/agent/chat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  });
  
  const result = await response.json();
  
  // 执行返回的 Excel 操作
  for (const operation of result.excel_operations) {
    if (operation.js_code) {
      await Excel.run(async (context) => {
        eval(operation.js_code);
      });
    }
  }
};
```

### 2. 安全执行代码

建议在前端添加代码安全校验：

```typescript
const safeExecute = (jsCode: string) => {
  // 1. 白名单检查
  const allowedPatterns = [
    /Excel\.run/,
    /context\.workbook/,
    /getRange/,
    /charts\.add/
  ];
  
  // 2. 黑名单检查
  const forbiddenPatterns = [
    /eval\(/,
    /Function\(/,
    /document\./,
    /window\./
  ];
  
  // 3. 执行校验通过的代码
  if (isCodeSafe(jsCode)) {
    return Excel.run(async (context) => {
      eval(jsCode);
    });
  }
};
```

## 📈 性能优化建议

1. **批量操作** - 合并多个 Excel API 调用
2. **缓存机制** - 缓存常用工具和响应
3. **异步处理** - 大批量数据处理使用后台任务
4. **错误重试** - 网络或 API 调用失败时的重试机制

## 🔒 安全注意事项

1. **代码执行安全** - 严格校验生成的 JavaScript 代码
2. **权限控制** - 确保用户只能操作有权限的工作表
3. **输入验证** - 验证用户输入的范围和参数
4. **API 限流** - 防止滥用 AI API 调用

## 🐛 故障排除

### 常见问题

1. **Agent 初始化失败**
   - 检查 OpenAI API key 是否正确配置
   - 确认网络连接正常

2. **工具调用失败**
   - 检查 Excel API 参数格式
   - 确认目标工作表和范围存在

3. **前端执行失败**
   - 检查 Office.js 是否正确加载
   - 确认 Excel 插件权限设置

## 🎯 下一步开发计划

1. **增强工具集** - 添加更多 Excel 操作工具
2. **上下文记忆** - 支持多轮对话的上下文保持
3. **任务编排** - 复杂任务的自动分解和并行执行
4. **用户偏好学习** - 根据用户习惯优化操作建议

---

**🎉 恭喜！您已成功集成了 Excel 智能 Agent 基础框架！** 