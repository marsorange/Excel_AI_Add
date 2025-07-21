#!/usr/bin/env python3
"""
测试所有模块的导入
"""

print("开始测试导入...")

try:
    import sys
    print(f"Python版本: {sys.version}")
    print(f"当前路径: {sys.path}")
    
    print("\n1. 测试基础模块...")
    import os
    import sqlite3
    print("✓ 基础模块导入成功")
    
    print("\n2. 测试FastAPI相关...")
    from fastapi import FastAPI
    from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
    from fastapi.middleware.cors import CORSMiddleware
    print("✓ FastAPI模块导入成功")
    
    print("\n3. 测试数据库相关...")
    from sqlalchemy import create_engine, Column, Integer, String, Boolean, text
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    print("✓ SQLAlchemy模块导入成功")
    
    print("\n4. 测试加密相关...")
    from passlib.context import CryptContext
    from jose import JWTError, jwt
    print("✓ 加密模块导入成功")
    
    print("\n5. 测试自定义模块...")
    
    # 测试database模块
    import database
    print("✓ database模块导入成功")
    
    # 测试models模块
    import models
    print("✓ models模块导入成功")
    
    # 测试schemas模块
    import schemas
    print("✓ schemas模块导入成功")
    
    # 测试crud模块
    import crud
    print("✓ crud模块导入成功")
    
    # 测试config模块
    import config
    print("✓ config模块导入成功")
    
    # 测试dependencies模块
    import dependencies
    print("✓ dependencies模块导入成功")
    
    print("\n6. 测试数据库连接...")
    # 创建数据库表
    models.Base.metadata.create_all(bind=database.engine)
    print("✓ 数据库表创建成功")
    
    # 测试数据库连接
    db = database.SessionLocal()
    try:
        result = db.execute(text("SELECT 1")).fetchone()
        print(f"✓ 数据库连接测试成功: {result}")
    finally:
        db.close()
    
    print("\n7. 测试FastAPI应用...")
    import main
    print("✓ main模块导入成功")
    
    print("\n✅ 所有测试通过!")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc() 