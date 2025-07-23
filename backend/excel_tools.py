"""
Excel API 工具集封装模块
为 langGraph Agent 提供可调用的 Excel 操作工具
"""

from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import json


class ExcelOperation(BaseModel):
    """Excel 操作的基础模型"""
    operation_type: str
    target: str
    parameters: Dict[str, Any] = {}
    description: str = ""


class ReadRangeTool(BaseTool):
    """读取 Excel 单元格范围的工具"""
    name = "read_range"
    description = "读取 Excel 工作表中指定范围的单元格数据"
    
    def _run(self, sheet_name: str = "Sheet1", range_address: str = "A1:A10") -> str:
        """
        生成读取单元格范围的 Office.js 代码
        
        Args:
            sheet_name: 工作表名称
            range_address: 单元格范围地址，如 "A1:B10"
        
        Returns:
            JSON 格式的操作指令
        """
        operation = ExcelOperation(
            operation_type="read_range",
            target=f"{sheet_name}!{range_address}",
            parameters={
                "sheet_name": sheet_name,
                "range_address": range_address
            },
            description=f"读取工作表 {sheet_name} 中 {range_address} 范围的数据"
        )
        
        js_code = f"""
// 读取单元格范围数据
Excel.run(async (context) => {{
    const sheet = context.workbook.worksheets.getItem("{sheet_name}");
    const range = sheet.getRange("{range_address}");
    range.load("values");
    await context.sync();
    return range.values;
}});
"""
        
        return json.dumps({
            "operation": operation.dict(),
            "js_code": js_code,
            "success": True
        }, ensure_ascii=False, indent=2)
    
    async def _arun(self, sheet_name: str = "Sheet1", range_address: str = "A1:A10") -> str:
        return self._run(sheet_name, range_address)


class WriteRangeTool(BaseTool):
    """写入 Excel 单元格范围的工具"""
    name = "write_range"
    description = "向 Excel 工作表中指定范围写入数据"
    
    def _run(self, sheet_name: str = "Sheet1", range_address: str = "A1", 
             values: str = "[[1]]") -> str:
        """
        生成写入单元格范围的 Office.js 代码
        
        Args:
            sheet_name: 工作表名称
            range_address: 目标单元格范围
            values: 要写入的数据，JSON 格式的二维数组字符串
        
        Returns:
            JSON 格式的操作指令
        """
        try:
            # 解析值数据
            values_array = json.loads(values) if isinstance(values, str) else values
        except:
            values_array = [[values]]
        
        operation = ExcelOperation(
            operation_type="write_range",
            target=f"{sheet_name}!{range_address}",
            parameters={
                "sheet_name": sheet_name,
                "range_address": range_address,
                "values": values_array
            },
            description=f"向工作表 {sheet_name} 中 {range_address} 写入数据"
        )
        
        js_code = f"""
// 写入单元格范围数据
Excel.run(async (context) => {{
    const sheet = context.workbook.worksheets.getItem("{sheet_name}");
    const range = sheet.getRange("{range_address}");
    range.values = {json.dumps(values_array)};
    await context.sync();
    return "数据写入成功";
}});
"""
        
        return json.dumps({
            "operation": operation.dict(),
            "js_code": js_code,
            "success": True
        }, ensure_ascii=False, indent=2)
    
    async def _arun(self, sheet_name: str = "Sheet1", range_address: str = "A1", 
                    values: str = "[[1]]") -> str:
        return self._run(sheet_name, range_address, values)


class FormulaGeneratorTool(BaseTool):
    """Excel 公式生成工具"""
    name = "generate_formula"
    description = "根据自然语言描述生成 Excel 公式"
    
    def _run(self, description: str, target_cell: str = "A1", 
             sheet_name: str = "Sheet1") -> str:
        """
        根据描述生成公式
        
        Args:
            description: 公式功能的自然语言描述
            target_cell: 目标单元格
            sheet_name: 工作表名称
        
        Returns:
            包含公式的操作指令
        """
        # 这里可以集成更复杂的公式生成逻辑
        # 目前先提供一个简单的示例
        
        formula_examples = {
            "求和": "=SUM(A1:A10)",
            "平均值": "=AVERAGE(A1:A10)",
            "最大值": "=MAX(A1:A10)",
            "最小值": "=MIN(A1:A10)",
            "计数": "=COUNT(A1:A10)",
            "条件求和": "=SUMIF(A1:A10,\">100\")",
            "条件计数": "=COUNTIF(A1:A10,\">0\")"
        }
        
        # 简单的关键词匹配
        formula = "=SUM(A1:A10)"  # 默认公式
        for key, value in formula_examples.items():
            if key in description:
                formula = value
                break
        
        operation = ExcelOperation(
            operation_type="set_formula",
            target=f"{sheet_name}!{target_cell}",
            parameters={
                "sheet_name": sheet_name,
                "target_cell": target_cell,
                "formula": formula,
                "description": description
            },
            description=f"在 {sheet_name} 的 {target_cell} 单元格设置公式: {formula}"
        )
        
        js_code = f"""
// 设置单元格公式
Excel.run(async (context) => {{
    const sheet = context.workbook.worksheets.getItem("{sheet_name}");
    const range = sheet.getRange("{target_cell}");
    range.formulas = [["{formula}"]];
    await context.sync();
    return "公式设置成功: {formula}";
}});
"""
        
        return json.dumps({
            "operation": operation.dict(),
            "js_code": js_code,
            "success": True,
            "formula": formula
        }, ensure_ascii=False, indent=2)
    
    async def _arun(self, description: str, target_cell: str = "A1", 
                    sheet_name: str = "Sheet1") -> str:
        return self._run(description, target_cell, sheet_name)


class CreateChartTool(BaseTool):
    """创建图表工具"""
    name = "create_chart"
    description = "基于指定数据范围创建图表"
    
    def _run(self, data_range: str = "A1:B10", chart_type: str = "Column", 
             sheet_name: str = "Sheet1", chart_title: str = "图表") -> str:
        """
        创建图表
        
        Args:
            data_range: 数据范围
            chart_type: 图表类型 (Column, Line, Pie 等)
            sheet_name: 工作表名称
            chart_title: 图表标题
        
        Returns:
            创建图表的操作指令
        """
        operation = ExcelOperation(
            operation_type="create_chart",
            target=f"{sheet_name}!{data_range}",
            parameters={
                "sheet_name": sheet_name,
                "data_range": data_range,
                "chart_type": chart_type,
                "chart_title": chart_title
            },
            description=f"在工作表 {sheet_name} 中基于 {data_range} 数据创建 {chart_type} 图表"
        )
        
        js_code = f"""
// 创建图表
Excel.run(async (context) => {{
    const sheet = context.workbook.worksheets.getItem("{sheet_name}");
    const dataRange = sheet.getRange("{data_range}");
    const chart = sheet.charts.add(Excel.ChartType.{chart_type.lower()}, dataRange);
    chart.title.text = "{chart_title}";
    chart.legend.position = Excel.ChartLegendPosition.right;
    await context.sync();
    return "图表创建成功";
}});
"""
        
        return json.dumps({
            "operation": operation.dict(),
            "js_code": js_code,
            "success": True
        }, ensure_ascii=False, indent=2)
    
    async def _arun(self, data_range: str = "A1:B10", chart_type: str = "Column", 
                    sheet_name: str = "Sheet1", chart_title: str = "图表") -> str:
        return self._run(data_range, chart_type, sheet_name, chart_title)


# 工具集合
def get_excel_tools() -> List[BaseTool]:
    """获取所有 Excel 工具"""
    tools: List[BaseTool] = [
        ReadRangeTool(),
        WriteRangeTool(), 
        FormulaGeneratorTool(),
        CreateChartTool()
    ]
    return tools


# 工具描述，用于 Agent 选择合适的工具
TOOL_DESCRIPTIONS = {
    "read_range": "读取 Excel 单元格范围数据，适用于需要获取现有数据的场景",
    "write_range": "向 Excel 单元格写入数据，适用于需要输出结果或填充数据的场景",
    "generate_formula": "生成 Excel 公式，适用于需要进行计算或数据处理的场景",
    "create_chart": "创建图表，适用于需要数据可视化的场景"
} 