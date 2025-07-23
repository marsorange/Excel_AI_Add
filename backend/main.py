from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import crud, models, schemas, database, dependencies
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta
from jose import jwt
import re
import os
import httpx
import time
import json
from dotenv import load_dotenv
from llm_config import get_llm_config, call_llm, check_llm_config

models.Base.metadata.create_all(bind=database.engine)
load_dotenv()

app = FastAPI(title="Excel AI 用户认证API")

# 添加CORS中间件，允许本地前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "https://localhost:3000",
        "http://127.0.0.1:3000",
        "https://127.0.0.1:3000",
        "https://localhost:8000",  # 添加后端 HTTPS 支持
        "http://localhost:8000"   # 保持 HTTP 兼容性
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取LLM配置
llm_config = get_llm_config()

async def call_llm_with_excel_context(user_message: str) -> str:
    """调用 LLM API 进行Excel相关对话"""
    try:
        # 构建系统提示词，专门针对 Excel 操作
        system_prompt = """你是一个专业的 Excel 财务助手。你的任务是理解用户的 Excel 需求，特别是财务相关的操作，并提供清晰的解决方案。

你应该：
1. 用简洁明了的中文回复用户
2. 如果用户需要 Excel 操作，描述具体的操作步骤
3. 对于财务相关需求，提供专业的会计和财务指导
4. 保持专业和友好的语调

用户的需求可能包括：

**基础功能：**
- 公式生成和解释
- 数据筛选和排序  
- 图表创建
- 数据分析
- 格式化操作

**财务专业功能：**
- 凭证录入：创建标准会计凭证录入模板，包括科目、借贷方向、金额等
- 表格对账：对比两个数据表格，找出差异，生成对账报告
- 数据清洗：清理财务数据，去除重复项，统一格式，处理异常值
- 三大报表生成：创建资产负债表、利润表、现金流量表的标准模板

当用户提到财务相关需求时，我会自动生成相应的Excel操作代码来帮助完成任务。

请根据用户输入提供最合适的建议。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return await call_llm(messages, temperature=0.7, max_tokens=1000)
        
    except Exception as e:
        print(f"LLM API 调用失败: {e}")
        return "抱歉，处理您的请求时出现错误，请稍后重试。"

def parse_llm_response(user_message: str, ai_response: str) -> list:
    """解析 LLM 响应并生成相应的 Excel 操作"""
    excel_operations = []
    
    # 简单的关键词匹配来生成操作
    user_message_lower = user_message.lower().strip()
    ai_response_lower = ai_response.lower()
    
    # 检查是否是简单对话，不需要 Excel 操作
    simple_chat_keywords = [
        "你好", "hi", "hello", "嗨", "您好",
        "谢谢", "thanks", "thank you", "感谢",
        "你是谁", "你能做什么", "帮助", "help",
        "再见", "bye", "goodbye", "拜拜"
    ]
    
    # 如果是简单问候且消息很短，直接返回空操作列表
    is_simple_chat = False
    for keyword in simple_chat_keywords:
        if keyword in user_message_lower and len(user_message.strip()) <= 10:
            is_simple_chat = True
            break
    
    if is_simple_chat:
        return []  # 不生成任何 Excel 操作
    
    # 检查财务相关功能
    # 凭证录入功能
    if any(keyword in user_message_lower for keyword in ["凭证录入", "凭证", "会计凭证", "借贷", "科目"]):
        excel_operations.append({
            "operation_type": "voucher_entry_template",
            "description": "创建会计凭证录入模板",
            "js_code": """Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    
    // 设置标题
    const titleRange = sheet.getRange("A1:F1");
    titleRange.merge();
    titleRange.values = [["会计凭证录入模板"]];
    titleRange.format.font.bold = true;
    titleRange.format.font.size = 14;
    titleRange.format.horizontalAlignment = "Center";
    
    // 设置表头
    const headerRange = sheet.getRange("A3:F3");
    headerRange.values = [["日期", "凭证号", "科目代码", "科目名称", "借方金额", "贷方金额"]];
    headerRange.format.font.bold = true;
    headerRange.format.fill.color = "#E7E6E6";
    headerRange.format.borders.getItem("EdgeAround").style = "Continuous";
    
    // 设置数据区域格式
    const dataRange = sheet.getRange("A4:F20");
    dataRange.format.borders.getItem("EdgeAround").style = "Continuous";
    dataRange.format.borders.getItem("InsideHorizontal").style = "Continuous";
    dataRange.format.borders.getItem("InsideVertical").style = "Continuous";
    
    // 设置数值格式
    sheet.getRange("E4:F20").numberFormat = [["#,##0.00"]];
    
    // 设置日期格式
    sheet.getRange("A4:A20").numberFormat = [["yyyy-mm-dd"]];
    
    // 调整列宽
    sheet.getRange("A:A").columnWidth = 80;
    sheet.getRange("B:B").columnWidth = 80;
    sheet.getRange("C:C").columnWidth = 80;
    sheet.getRange("D:D").columnWidth = 120;
    sheet.getRange("E:E").columnWidth = 100;
    sheet.getRange("F:F").columnWidth = 100;
    
    await context.sync();
    console.log("会计凭证录入模板已创建");
});""",
            "parameters": {"template_type": "voucher_entry", "range": "A1:F20"}
        })
    
    # 表格对账功能
    if any(keyword in user_message_lower for keyword in ["对账", "表格对账", "对比", "差异", "匹配"]):
        excel_operations.append({
            "operation_type": "reconciliation_analysis",
            "description": "创建表格对账分析模板",
            "js_code": """Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    
    // 创建对账分析标题
    const titleRange = sheet.getRange("A1:E1");
    titleRange.merge();
    titleRange.values = [["表格对账分析"]];
    titleRange.format.font.bold = true;
    titleRange.format.font.size = 16;
    titleRange.format.horizontalAlignment = "Center";
    
    // 左表标题
    const leftTableTitle = sheet.getRange("A3:C3");
    leftTableTitle.merge();
    leftTableTitle.values = [["表格A（基础数据）"]];
    leftTableTitle.format.font.bold = true;
    leftTableTitle.format.fill.color = "#D5E8FF";
    
    // 右表标题
    const rightTableTitle = sheet.getRange("F3:H3");
    rightTableTitle.merge();
    rightTableTitle.values = [["表格B（对比数据）"]];
    rightTableTitle.format.font.bold = true;
    rightTableTitle.format.fill.color = "#FFE6CC";
    
    // 差异分析标题
    const diffTitle = sheet.getRange("J3:L3");
    diffTitle.merge();
    diffTitle.values = [["差异分析"]];
    diffTitle.format.font.bold = true;
    diffTitle.format.fill.color = "#F2D5D5";
    
    // 设置表头
    sheet.getRange("A4:C4").values = [["编号", "项目", "金额"]];
    sheet.getRange("F4:H4").values = [["编号", "项目", "金额"]];
    sheet.getRange("J4:L4").values = [["编号", "差异类型", "差异金额"]];
    
    // 添加对账公式示例
    sheet.getRange("J5").values = [["=IF(A5<>F5,\"编号不匹配\",IF(C5<>H5,\"金额差异\",\"匹配\"))"]];
    sheet.getRange("L5").values = [["=C5-H5"]];
    
    await context.sync();
    console.log("表格对账分析模板已创建");
});""",
            "parameters": {"template_type": "reconciliation", "range": "A1:L20"}
        })
    
    # 数据清洗功能
    if any(keyword in user_message_lower for keyword in ["数据清洗", "清洗", "去重", "格式", "异常值"]):
        excel_operations.append({
            "operation_type": "data_cleaning",
            "description": "数据清洗和格式化",
            "js_code": """Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const usedRange = sheet.getUsedRange();
    
    if (usedRange) {
        usedRange.load("values,rowCount,columnCount");
        await context.sync();
        
        // 去除空行
        for (let i = usedRange.rowCount - 1; i >= 0; i--) {
            const rowRange = usedRange.getRow(i);
            rowRange.load("values");
            await context.sync();
            
            // 检查是否为空行
            const isEmpty = rowRange.values[0].every(cell => cell === "" || cell === null);
            if (isEmpty) {
                sheet.getRange(`${i + 1}:${i + 1}`).delete("Up");
            }
        }
        
        // 数据格式标准化
        const dataRange = sheet.getUsedRange();
        dataRange.load("columnCount");
        await context.sync();
        
        // 假设第一列是日期格式
        sheet.getUsedRange().getColumn(0).numberFormat = [["yyyy-mm-dd"]];
        
        // 假设最后几列是金额格式
        for (let i = Math.max(0, dataRange.columnCount - 3); i < dataRange.columnCount; i++) {
            sheet.getUsedRange().getColumn(i).numberFormat = [["#,##0.00"]];
        }
        
        console.log("数据清洗完成");
    }
    
    await context.sync();
});""",
            "parameters": {"operation": "data_cleaning"}
        })
    
    # 三大报表生成功能  
    if any(keyword in user_message_lower for keyword in ["三大报表", "财务报表", "资产负债表", "利润表", "现金流量表"]):
        excel_operations.append({
            "operation_type": "financial_reports",
            "description": "生成财务三大报表模板",
            "js_code": """Excel.run(async (context) => {
    const workbook = context.workbook;
    
    // 创建资产负债表工作表
    let balanceSheet;
    try {
        balanceSheet = workbook.worksheets.getItem("资产负债表");
    } catch {
        balanceSheet = workbook.worksheets.add("资产负债表");
    }
    
    // 设置资产负债表
    balanceSheet.getRange("A1").values = [["资产负债表"]];
    balanceSheet.getRange("A1").format.font.bold = true;
    balanceSheet.getRange("A1").format.font.size = 16;
    
    // 资产部分
    balanceSheet.getRange("A3:C3").values = [["资产", "", "金额"]];
    balanceSheet.getRange("A4:C8").values = [
        ["流动资产", "", ""],
        ["  货币资金", "", ""],
        ["  应收账款", "", ""],
        ["  存货", "", ""],
        ["非流动资产", "", ""]
    ];
    
    // 负债及所有者权益部分  
    balanceSheet.getRange("A10:C10").values = [["负债及所有者权益", "", "金额"]];
    balanceSheet.getRange("A11:C15").values = [
        ["流动负债", "", ""],
        ["  应付账款", "", ""],
        ["  短期借款", "", ""],
        ["所有者权益", "", ""],
        ["  实收资本", "", ""]
    ];
    
    // 创建利润表工作表
    let incomeStatement;
    try {
        incomeStatement = workbook.worksheets.getItem("利润表");
    } catch {
        incomeStatement = workbook.worksheets.add("利润表");
    }
    
    // 设置利润表
    incomeStatement.getRange("A1").values = [["利润表"]];
    incomeStatement.getRange("A1").format.font.bold = true;
    incomeStatement.getRange("A1").format.font.size = 16;
    
    incomeStatement.getRange("A3:B3").values = [["项目", "金额"]];
    incomeStatement.getRange("A4:B10").values = [
        ["营业收入", ""],
        ["营业成本", ""],
        ["营业利润", "=A4-A5"],
        ["营业外收入", ""],
        ["营业外支出", ""],
        ["利润总额", "=A6+A7-A8"],
        ["所得税费用", ""]
    ];
    
    // 创建现金流量表工作表
    let cashFlow;
    try {
        cashFlow = workbook.worksheets.getItem("现金流量表");
    } catch {
        cashFlow = workbook.worksheets.add("现金流量表");
    }
    
    // 设置现金流量表
    cashFlow.getRange("A1").values = [["现金流量表"]];
    cashFlow.getRange("A1").format.font.bold = true;
    cashFlow.getRange("A1").format.font.size = 16;
    
    cashFlow.getRange("A3:B3").values = [["项目", "金额"]];
    cashFlow.getRange("A4:B10").values = [
        ["经营活动现金流入", ""],
        ["经营活动现金流出", ""],
        ["经营活动产生的现金流量净额", "=A4-A5"],
        ["投资活动产生的现金流量净额", ""],
        ["筹资活动产生的现金流量净额", ""],
        ["现金及现金等价物净增加额", "=A6+A7+A8"],
        ["期初现金余额", ""]
    ];
    
    await context.sync();
    console.log("财务三大报表模板已创建");
});""",
            "parameters": {"reports": ["balance_sheet", "income_statement", "cash_flow"]}
        })
    
    # 检查是否需要生成公式
    if any(keyword in user_message_lower for keyword in ["求和", "总和", "sum", "公式", "计算"]):
        excel_operations.append({
            "operation_type": "generate_formula",
            "description": "生成求和公式",
            "js_code": """Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const range = sheet.getRange("A1");
    range.formulas = [["=SUM(A1:A10)"]];
    await context.sync();
    console.log("求和公式已生成");
});""",
            "parameters": {"formula": "=SUM(A1:A10)", "target_cell": "A1"}
        })
    
    # 检查是否需要读取数据
    if any(keyword in user_message_lower for keyword in ["读取", "查看", "显示", "数据", "分析"]):
        excel_operations.append({
            "operation_type": "read_range",
            "description": "读取数据范围",
            "js_code": """Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const range = sheet.getRange("A1:A10");
    range.load("values");
    await context.sync();
    console.log("数据已读取:", range.values);
});""",
            "parameters": {"range": "A1:A10"}
        })
    
    # 检查是否需要创建图表
    if any(keyword in user_message_lower for keyword in ["图表", "chart", "图", "可视化"]):
        excel_operations.append({
            "operation_type": "create_chart",
            "description": "创建柱状图",
            "js_code": """Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const dataRange = sheet.getRange("A1:B10");
    const chart = sheet.charts.add(Excel.ChartType.columnClustered, dataRange);
    chart.title.text = "数据图表";
    chart.legend.position = Excel.ChartLegendPosition.right;
    await context.sync();
    console.log("图表创建成功");
});""",
            "parameters": {"chart_type": "column", "data_range": "A1:B10", "title": "数据图表"}
        })
    
    # 只有在检测到明确的 Excel 相关关键词时才提供通用操作
    excel_keywords = [
        "excel", "表格", "单元格", "工作表", "行", "列", 
        "vlookup", "pivot", "透视表", "筛选", "排序"
    ]
    
    has_excel_keywords = any(keyword in user_message_lower for keyword in excel_keywords)
    
    # 如果没有匹配到特定操作但包含 Excel 关键词，提供一个通用的信息操作
    if not excel_operations and has_excel_keywords:
        excel_operations.append({
            "operation_type": "info",
            "description": "查看当前工作表信息",
            "js_code": """Excel.run(async (context) => {
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    sheet.load("name");
    await context.sync();
    console.log("当前工作表:", sheet.name);
});""",
            "parameters": {"action": "get_sheet_info"}
        })
    
    return excel_operations

# 注册接口
@app.post("/register", response_model=schemas.User)
async def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(user.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    if not re.search(r'[a-zA-Z]', user.password):
        raise HTTPException(status_code=400, detail="Password must contain English characters")
    return crud.create_user(db=db, user=user)

# 登录接口
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    hashed_password = getattr(user, 'hashed_password', None)
    if not user or not isinstance(hashed_password, str) or not crud.verify_password(form_data.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = jwt.encode({"sub": user.email}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

# 获取当前用户信息
@app.get("/users/me", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(dependencies.get_current_user)):
    return current_user

# 公式生成
@app.post("/api/generate-formula", response_model=schemas.FormulaResponse)
async def generate_formula(request: schemas.NLToFormulaRequest, current_user: schemas.User = Depends(dependencies.get_current_user)):
    if not check_llm_config():
        raise HTTPException(status_code=500, detail="LLM API 配置无效")
    
    try:
        messages = [
            {"role": "system", "content": "You are an AI assistant that generates Excel formulas from natural language descriptions. Provide only the formula, without any additional text or explanation. If you cannot generate a formula, respond with 'Error: Could not generate formula.'"},
            {"role": "user", "content": request.text}
        ]
        
        generated_formula = await call_llm(messages)
        
        if generated_formula.lower().startswith("error:"):
            raise HTTPException(status_code=500, detail=generated_formula)
        
        return schemas.FormulaResponse(formula=generated_formula.strip())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成公式时出错: {str(e)}")

# 公式解释
@app.post("/api/explain-formula", response_model=schemas.ExplainFormulaResponse)
async def explain_formula(request: schemas.ExplainFormulaRequest, current_user: schemas.User = Depends(dependencies.get_current_user)):
    if not check_llm_config():
        raise HTTPException(status_code=500, detail="LLM API 配置无效")
    
    try:
        messages = [
            {"role": "system", "content": "You are an AI assistant that explains Excel formulas in a clear and concise manner. Provide only the explanation, without any additional text or introduction."},
            {"role": "user", "content": f"Explain the Excel formula: {request.formula}"}
        ]
        
        explanation = await call_llm(messages)
        return schemas.ExplainFormulaResponse(explanation=explanation.strip())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解释公式时出错: {str(e)}")

# 公式优化
@app.post("/api/optimize-formula", response_model=schemas.OptimizeFormulaResponse)
async def optimize_formula(request: schemas.OptimizeFormulaRequest, current_user: schemas.User = Depends(dependencies.get_current_user)):
    if not check_llm_config():
        raise HTTPException(status_code=500, detail="LLM API 配置无效")
    
    try:
        messages = [
            {"role": "system", "content": "You are an AI assistant that optimizes Excel formulas. Provide the optimized formula and a brief explanation of the optimization. Format your response as: Optimized Formula: [formula]\nExplanation: [explanation]."},
            {"role": "user", "content": f"Optimize the Excel formula: {request.formula}"}
        ]
        
        content = await call_llm(messages)
        
        optimized_formula = ""
        explanation = ""
        lines = content.split('\n')
        for line in lines:
            if line.startswith("Optimized Formula:"):
                optimized_formula = line.replace("Optimized Formula:", "").strip()
            elif line.startswith("Explanation:"):
                explanation = line.replace("Explanation:", "").strip()
        
        if not optimized_formula or not explanation:
            raise HTTPException(status_code=500, detail="LLM API返回了无法解析的优化格式")
        
        return schemas.OptimizeFormulaResponse(
            original_formula=request.formula,
            suggested_formula=optimized_formula,
            explanation=explanation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"优化公式时出错: {str(e)}")

# 公式错误诊断
@app.post("/api/diagnose-error", response_model=schemas.DiagnoseErrorResponse)
async def diagnose_error(request: schemas.DiagnoseErrorRequest, current_user: schemas.User = Depends(dependencies.get_current_user)):
    if not check_llm_config():
        raise HTTPException(status_code=500, detail="LLM API 配置无效")
    
    try:
        messages = [
            {"role": "system", "content": "You are an AI assistant that diagnoses errors in Excel formulas and suggests fixes. Provide the error type, explanation, and suggested fix. Format your response as: Error Type: [type]\nExplanation: [explanation]\nSuggested Fix: [fix]."},
            {"role": "user", "content": f"Diagnose the error in this Excel formula: {request.formula}"}
        ]
        
        content = await call_llm(messages)
        
        error_type = ""
        explanation = ""
        suggested_fix = ""
        lines = content.split('\n')
        for line in lines:
            if line.startswith("Error Type:"):
                error_type = line.replace("Error Type:", "").strip()
            elif line.startswith("Explanation:"):
                explanation = line.replace("Explanation:", "").strip()
            elif line.startswith("Suggested Fix:"):
                suggested_fix = line.replace("Suggested Fix:", "").strip()
        
        if not error_type or not explanation or not suggested_fix:
            raise HTTPException(status_code=500, detail="LLM API返回了无法解析的诊断格式")
        
        return schemas.DiagnoseErrorResponse(
            error_type=error_type,
            explanation=explanation,
            suggested_fix=suggested_fix
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"诊断公式错误时出错: {str(e)}")

# Agent 对话接口
@app.post("/agent/chat")
async def agent_chat(
    request: schemas.AgentChatRequest,
    current_user: schemas.User = Depends(dependencies.get_current_user)
):
    """
    Agent 智能对话接口
    用户可以输入自然语言，Agent 自动规划并生成 Excel 操作
    """
    try:
        if not check_llm_config():
            raise HTTPException(status_code=500, detail="LLM API 配置无效")
        
        # 调用 LLM API 进行对话
        llm_response = await call_llm_with_excel_context(request.message)
        
        # 解析响应并生成 Excel 操作
        excel_operations = parse_llm_response(request.message, llm_response)
        
        response_data = {
            "success": True,
            "response": llm_response,
            "excel_operations": excel_operations,
            "conversation_id": request.conversation_id or f"conv_{int(time.time())}"
        }
        
        return schemas.AgentChatResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Agent 处理请求时出错: {str(e)}"
        )

# LLM配置信息接口
@app.get("/api/llm-info")
async def get_llm_info(current_user: schemas.User = Depends(dependencies.get_current_user)):
    """获取当前LLM配置信息"""
    return llm_config.get_provider_info()

# HTTPS 启动配置
if __name__ == "__main__":
    import uvicorn
    import ssl
    import os
    from pathlib import Path
    
    # 查找证书文件 - 优先查找用户目录下的证书
    cert_file = None
    key_file = None
    
    # 检查可能的证书文件位置（按优先级顺序）
    possible_cert_paths = [
        Path.home() / ".office-addin-dev-certs" / "localhost.crt",
        Path.home() / ".office-addin-dev-certs" / "ca.crt",
        Path(__file__).parent.parent / "localhost.crt",
        Path(__file__).parent.parent / "localhost.pem"
    ]
    
    possible_key_paths = [
        Path.home() / ".office-addin-dev-certs" / "localhost.key", 
        Path.home() / ".office-addin-dev-certs" / "ca.key",
        Path(__file__).parent.parent / "localhost-key.pem",
        Path(__file__).parent.parent / "localhost.key"
    ]
    
    # 寻找证书文件
    for cert_path in possible_cert_paths:
        if cert_path.exists():
            cert_file = str(cert_path)
            print(f"找到证书文件: {cert_file}")
            break
    
    # 寻找私钥文件
    for key_path in possible_key_paths:
        if key_path.exists():
            key_file = str(key_path)
            print(f"找到私钥文件: {key_file}")
            break
    
    if cert_file and key_file:
        print("🔒 启动 HTTPS 服务器...")
        try:
            uvicorn.run(
                "main:app", 
                host="0.0.0.0", 
                port=8000, 
                reload=True,
                ssl_keyfile=key_file,
                ssl_certfile=cert_file
            )
        except Exception as e:
            print(f"❌ HTTPS 启动失败: {e}")
            print("🔄 回退到 HTTP 模式...")
            uvicorn.run(
                "main:app", 
                host="0.0.0.0", 
                port=8000, 
                reload=True
            )
    else:
        print("⚠️  警告: 未找到证书文件，启动 HTTP 服务器...")
        print("💡 如需 HTTPS，请运行: npx office-addin-dev-certs install")
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True
        )