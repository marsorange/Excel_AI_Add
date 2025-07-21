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
from dotenv import load_dotenv

models.Base.metadata.create_all(bind=database.engine)
load_dotenv()

app = FastAPI(title="Excel AI 用户认证API")

# 添加CORS中间件，允许本地前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DeepSeek API配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "你的API_KEY")
DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")

def check_api_key():
    if not DEEPSEEK_API_KEY or DEEPSEEK_API_KEY == "你的API_KEY":
        raise HTTPException(status_code=500, detail="DeepSeek API Key 未配置")

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
    check_api_key()
    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        messages = [
            {"role": "system", "content": "You are an AI assistant that generates Excel formulas from natural language descriptions. Provide only the formula, without any additional text or explanation. If you cannot generate a formula, respond with 'Error: Could not generate formula.'"},
            {"role": "user", "content": request.text}
        ]
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": False
        }
        try:
            response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            deepseek_response = response.json()
            if deepseek_response and deepseek_response["choices"] and deepseek_response["choices"][0]["message"]:
                generated_formula = deepseek_response["choices"][0]["message"]["content"].strip()
                if generated_formula.lower().startswith("error:"):
                    raise HTTPException(status_code=500, detail=generated_formula)
                return schemas.FormulaResponse(formula=generated_formula)
            else:
                raise HTTPException(status_code=500, detail="DeepSeek API returned an unexpected response format.")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error communicating with DeepSeek API: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"DeepSeek API returned an error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# 公式解释
@app.post("/api/explain-formula", response_model=schemas.ExplainFormulaResponse)
async def explain_formula(request: schemas.ExplainFormulaRequest, current_user: schemas.User = Depends(dependencies.get_current_user)):
    check_api_key()
    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        messages = [
            {"role": "system", "content": "You are an AI assistant that explains Excel formulas in a clear and concise manner. Provide only the explanation, without any additional text or introduction."},
            {"role": "user", "content": f"Explain the Excel formula: {request.formula}"}
        ]
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": False
        }
        try:
            response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            deepseek_response = response.json()
            if deepseek_response and deepseek_response["choices"] and deepseek_response["choices"][0]["message"]:
                explanation = deepseek_response["choices"][0]["message"]["content"].strip()
                return schemas.ExplainFormulaResponse(explanation=explanation)
            else:
                raise HTTPException(status_code=500, detail="DeepSeek API returned an unexpected response format.")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error communicating with DeepSeek API: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"DeepSeek API returned an error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# 公式优化
@app.post("/api/optimize-formula", response_model=schemas.OptimizeFormulaResponse)
async def optimize_formula(request: schemas.OptimizeFormulaRequest, current_user: schemas.User = Depends(dependencies.get_current_user)):
    check_api_key()
    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        messages = [
            {"role": "system", "content": "You are an AI assistant that optimizes Excel formulas. Provide the optimized formula and a brief explanation of the optimization. Format your response as: Optimized Formula: [formula]\nExplanation: [explanation]."},
            {"role": "user", "content": f"Optimize the Excel formula: {request.formula}"}
        ]
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": False
        }
        try:
            response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            deepseek_response = response.json()
            if deepseek_response and deepseek_response["choices"] and deepseek_response["choices"][0]["message"]:
                content = deepseek_response["choices"][0]["message"]["content"].strip()
                optimized_formula = ""
                explanation = ""
                lines = content.split('\n')
                for line in lines:
                    if line.startswith("Optimized Formula:"):
                        optimized_formula = line.replace("Optimized Formula:", "").strip()
                    elif line.startswith("Explanation:"):
                        explanation = line.replace("Explanation:", "").strip()
                if not optimized_formula or not explanation:
                    raise HTTPException(status_code=500, detail="DeepSeek API returned an unparseable optimization format.")
                return schemas.OptimizeFormulaResponse(
                    original_formula=request.formula,
                    suggested_formula=optimized_formula,
                    explanation=explanation
                )
            else:
                raise HTTPException(status_code=500, detail="DeepSeek API returned an unexpected response format.")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error communicating with DeepSeek API: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"DeepSeek API returned an error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# 公式错误诊断
@app.post("/api/diagnose-error", response_model=schemas.DiagnoseErrorResponse)
async def diagnose_error(request: schemas.DiagnoseErrorRequest, current_user: schemas.User = Depends(dependencies.get_current_user)):
    check_api_key()
    async with httpx.AsyncClient() as client:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        messages = [
            {"role": "system", "content": "You are an AI assistant that diagnoses errors in Excel formulas and suggests fixes. Provide the error type, explanation, and suggested fix. Format your response as: Error Type: [type]\nExplanation: [explanation]\nSuggested Fix: [fix]."},
            {"role": "user", "content": f"Diagnose the error in this Excel formula: {request.formula}"}
        ]
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": False
        }
        try:
            response = await client.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            deepseek_response = response.json()
            if deepseek_response and deepseek_response["choices"] and deepseek_response["choices"][0]["message"]:
                content = deepseek_response["choices"][0]["message"]["content"].strip()
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
                    raise HTTPException(status_code=500, detail="DeepSeek API returned an unparseable diagnosis format.")
                return schemas.DiagnoseErrorResponse(
                    error_type=error_type,
                    explanation=explanation,
                    suggested_fix=suggested_fix
                )
            else:
                raise HTTPException(status_code=500, detail="DeepSeek API returned an unexpected response format.")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Network error communicating with DeepSeek API: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"DeepSeek API returned an error: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")