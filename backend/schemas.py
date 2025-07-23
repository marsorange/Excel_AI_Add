from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# AI相关模型
class NLToFormulaRequest(BaseModel):
    text: str

class FormulaResponse(BaseModel):
    formula: str

class ExplainFormulaRequest(BaseModel):
    formula: str

class ExplainFormulaResponse(BaseModel):
    explanation: str

class OptimizeFormulaRequest(BaseModel):
    formula: str

class OptimizeFormulaResponse(BaseModel):
    original_formula: str
    suggested_formula: str
    explanation: str

class DiagnoseErrorRequest(BaseModel):
    formula: str

class DiagnoseErrorResponse(BaseModel):
    error_type: str
    explanation: str
    suggested_fix: str

# Agent 相关模型
class ExcelOperation(BaseModel):
    operation_type: str
    description: str
    js_code: Optional[str] = None
    parameters: Optional[dict] = None

class AgentChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[dict] = None

class AgentChatResponse(BaseModel):
    success: bool
    response: str
    excel_operations: list[ExcelOperation] = []
    conversation_id: Optional[str] = None
    error: Optional[str] = None
