"""
langGraph Agent 核心模块
实现基础对话 Agent 功能，可以自主调用 Excel API
"""

import os
from typing import Dict, Any, List, Optional, Annotated
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langgraph.graph.message import add_messages
from pydantic import BaseModel
import json
from excel_tools import get_excel_tools, TOOL_DESCRIPTIONS
from llm_config import get_llm_config, call_llm


class AgentState(BaseModel):
    """Agent 状态模型"""
    messages: Annotated[List[BaseMessage], add_messages]
    user_input: str = ""
    excel_operations: List[Dict[str, Any]] = []
    current_step: str = "start"
    error_message: str = ""


class ExcelAgent:
    """Excel 智能 Agent"""
    
    def __init__(self):
        """
        初始化 Agent
        使用统一的LLM配置
        """
        self.llm_config = get_llm_config()
        
        if not self.llm_config.check_api_key():
            raise ValueError(f"需要提供有效的 {self.llm_config.provider.upper()} API key")
        
        # 获取工具
        self.tools = get_excel_tools()
        self.tool_executor = ToolExecutor(self.tools)
        
        # 构建状态图
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """构建 Agent 工作流程图"""
        workflow = StateGraph(AgentState)
        
        # 添加节点
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", self._execute_tools)
        
        # 设置入口点
        workflow.set_entry_point("agent")
        
        # 添加条件边
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            }
        )
        
        # 工具执行后回到agent
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    async def _call_model(self, state: AgentState) -> AgentState:
        """调用语言模型"""
        try:
            # 构建系统消息
            system_message = self._get_system_prompt()
            
            # 准备消息列表
            messages = [
                {"role": "system", "content": system_message}
            ]
            
            # 添加历史消息
            for msg in state.messages:
                if isinstance(msg, HumanMessage):
                    messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages.append({"role": "assistant", "content": msg.content})
            
            # 如果没有用户输入，添加当前用户输入
            if state.user_input and not any(m["role"] == "user" for m in messages[-3:]):
                messages.append({"role": "user", "content": state.user_input})
            
            # 调用LLM
            response = await call_llm(messages, temperature=0.1, max_tokens=1500)
            
            # 创建AI消息
            ai_message = AIMessage(content=response)
            
            # 更新状态
            new_state = state.copy()
            new_state.messages = state.messages + [ai_message]
            
            # 检查是否需要调用工具
            if self._should_use_tools(response):
                new_state.current_step = "tools"
            else:
                new_state.current_step = "end"
            
            return new_state
            
        except Exception as e:
            error_msg = f"调用语言模型时出错: {str(e)}"
            error_state = state.copy()
            error_state.error_message = error_msg
            error_state.current_step = "end"
            return error_state
    
    def _execute_tools(self, state: AgentState) -> AgentState:
        """执行工具调用"""
        try:
            # 从最后的AI消息中提取工具调用
            last_message = state.messages[-1]
            if not isinstance(last_message, AIMessage):
                return state
            
            # 简单的工具调用检测和执行
            tools_used = []
            content = last_message.content.lower()
            
            # 检测需要的Excel操作
            if "读取" in content or "查看" in content:
                tool_result = self._execute_read_range_tool()
                tools_used.append(tool_result)
            
            if "公式" in content or "计算" in content:
                tool_result = self._execute_formula_tool(state.user_input)
                tools_used.append(tool_result)
            
            if "图表" in content or "chart" in content:
                tool_result = self._execute_chart_tool()
                tools_used.append(tool_result)
            
            # 更新状态
            new_state = state.copy()
            new_state.excel_operations.extend(tools_used)
            new_state.current_step = "agent"
            
            return new_state
            
        except Exception as e:
            error_state = state.copy()
            error_state.error_message = f"执行工具时出错: {str(e)}"
            error_state.current_step = "end"
            return error_state
    
    def _should_continue(self, state: AgentState) -> str:
        """判断是否继续工作流"""
        if state.error_message:
            return "end"
        
        if state.current_step == "tools":
            return "continue"
        
        return "end"
    
    def _should_use_tools(self, response: str) -> bool:
        """判断是否需要使用工具"""
        tool_keywords = [
            "读取", "查看", "数据", "公式", "计算", "图表", "chart",
            "单元格", "工作表", "范围", "创建", "生成"
        ]
        
        response_lower = response.lower()
        return any(keyword in response_lower for keyword in tool_keywords)
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的Excel AI助手。你可以帮助用户：

1. 理解和解释Excel公式
2. 生成Excel公式
3. 读取和分析Excel数据
4. 创建图表和可视化
5. 提供Excel操作指导

可用的Excel工具：
""" + TOOL_DESCRIPTIONS + """

请根据用户需求，提供准确的帮助和指导。如果需要执行Excel操作，我会调用相应的工具来完成。
"""
    
    def _execute_read_range_tool(self) -> Dict[str, Any]:
        """执行读取范围工具"""
        return {
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
        }
    
    def _execute_formula_tool(self, user_input: str) -> Dict[str, Any]:
        """执行公式工具"""
        # 简单的公式检测
        if "求和" in user_input or "sum" in user_input.lower():
            formula = "=SUM(A1:A10)"
        else:
            formula = "=A1+B1"
        
        return {
            "operation_type": "generate_formula",
            "description": "生成Excel公式",
            "js_code": f"""Excel.run(async (context) => {{
    const sheet = context.workbook.worksheets.getActiveWorksheet();
    const range = sheet.getRange("C1");
    range.formulas = [["{formula}"]];
    await context.sync();
    console.log("公式已生成: {formula}");
}});""",
            "parameters": {"formula": formula, "target_cell": "C1"}
        }
    
    def _execute_chart_tool(self) -> Dict[str, Any]:
        """执行图表工具"""
        return {
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
        }
    
    async def chat(self, user_input: str) -> Dict[str, Any]:
        """与Agent对话"""
        try:
            # 创建初始状态
            initial_state = AgentState(
                messages=[HumanMessage(content=user_input)],
                user_input=user_input,
                excel_operations=[],
                current_step="start"
            )
            
            # 运行工作流
            result = await self.workflow.ainvoke(initial_state)
            
            # 提取响应
            last_message = result.messages[-1] if result.messages else None
            response_text = last_message.content if last_message and isinstance(last_message, AIMessage) else "抱歉，我无法处理您的请求。"
            
            return {
                "success": not bool(result.error_message),
                "response": response_text,
                "excel_operations": result.excel_operations,
                "error": result.error_message if result.error_message else None
            }
            
        except Exception as e:
            return {
                "success": False,
                "response": "抱歉，处理您的请求时出现了错误。",
                "excel_operations": [],
                "error": str(e)
            }


# 全局Agent实例
_agent_instance = None


def get_agent() -> ExcelAgent:
    """获取全局Agent实例"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = ExcelAgent()
    return _agent_instance


async def chat_with_agent(user_input: str) -> Dict[str, Any]:
    """便捷的Agent对话函数"""
    agent = get_agent()
    return await agent.chat(user_input) 