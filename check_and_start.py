#!/usr/bin/env python3
"""
项目完整性检查和启动脚本
检查前后端配置，确保项目可以正确运行
"""

import subprocess
import sys
import os
import json
from pathlib import Path
import time
import threading

def print_section(title):
    """打印分节标题"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    if Path(file_path).exists():
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description} 缺失: {file_path}")
        return False

def check_backend():
    """检查后端配置"""
    print_section("检查后端配置")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("✗ backend 目录不存在")
        return False
    
    # 检查必要文件
    required_files = [
        ("backend/main.py", "主应用文件"),
        ("backend/models.py", "数据模型"),
        ("backend/schemas.py", "数据模式"),
        ("backend/database.py", "数据库配置"),
        ("backend/crud.py", "数据库操作"),
        ("backend/dependencies.py", "依赖注入"),
        ("backend/config.py", "配置文件"),
        ("backend/requirements.txt", "依赖列表"),
    ]
    
    all_files_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    # 检查环境变量文件
    env_file = backend_dir / ".env"
    if env_file.exists():
        print("✓ 环境变量文件存在")
        # 读取并检查关键配置
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
                if "DEEPSEEK_API_KEY" in env_content:
                    print("✓ DeepSeek API Key 配置存在")
                else:
                    print("⚠ DeepSeek API Key 未配置")
        except Exception as e:
            print(f"⚠ 读取环境变量文件失败: {e}")
    else:
        print("⚠ .env 文件不存在，将使用默认配置")
    
    return all_files_exist

def check_frontend():
    """检查前端配置"""
    print_section("检查前端配置")
    
    # 检查必要文件
    required_files = [
        ("package.json", "包配置文件"),
        ("webpack.config.js", "Webpack配置"),
        ("manifest.xml", "Office插件清单"),
        ("src/taskpane/components/App.tsx", "主应用组件"),
        ("src/config/api.ts", "API配置文件"),
    ]
    
    all_files_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_files_exist = False
    
    # 检查图标文件
    icon_files = [
        "assets/icon-16.png",
        "assets/icon-32.png", 
        "assets/icon-80.png"
    ]
    
    for icon_file in icon_files:
        check_file_exists(icon_file, f"图标文件")
    
    return all_files_exist

def check_dependencies():
    """检查依赖"""
    print_section("检查依赖")
    
    # 检查Python
    print(f"✓ Python版本: {sys.version}")
    
    # 检查Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Node.js版本: {result.stdout.strip()}")
        else:
            print("✗ Node.js 未安装")
            return False
    except FileNotFoundError:
        print("✗ Node.js 未安装")
        return False
    
    # 检查npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ npm版本: {result.stdout.strip()}")
        else:
            print("✗ npm 未安装")
            return False
    except FileNotFoundError:
        print("✗ npm 未安装")
        return False
    
    return True

def install_backend_deps():
    """安装后端依赖"""
    print_section("安装后端依赖")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"
        ], check=True)
        print("✓ 后端依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 后端依赖安装失败: {e}")
        return False

def install_frontend_deps():
    """安装前端依赖"""
    print_section("安装前端依赖")
    
    try:
        subprocess.run(["npm", "install"], check=True)
        print("✓ 前端依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 前端依赖安装失败: {e}")
        return False

def start_backend_server():
    """启动后端服务器"""
    print("启动后端服务器...")
    try:
        subprocess.run([
            "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], cwd="backend")
    except KeyboardInterrupt:
        print("后端服务器已停止")
    except Exception as e:
        print(f"后端服务器启动失败: {e}")

def start_frontend_server():
    """启动前端服务器"""
    print("启动前端服务器...")
    try:
        subprocess.run(["npm", "run", "dev-server"])
    except KeyboardInterrupt:
        print("前端服务器已停止")
    except Exception as e:
        print(f"前端服务器启动失败: {e}")

def main():
    """主函数"""
    print("=== Excel AI 助手项目检查和启动脚本 ===")
    
    # 检查项目完整性
    backend_ok = check_backend()
    frontend_ok = check_frontend()
    deps_ok = check_dependencies()
    
    if not (backend_ok and frontend_ok and deps_ok):
        print("\n❌ 项目检查失败，请修复上述问题后重试")
        return
    
    print("\n✅ 项目检查通过！")
    
    # 安装依赖
    if not install_backend_deps():
        return
    
    if not install_frontend_deps():
        return
    
    print_section("启动服务")
    print("即将启动前后端服务器...")
    print("后端: http://localhost:8000")
    print("前端: https://localhost:3000")
    print("\n请选择启动方式:")
    print("1. 同时启动前后端 (推荐)")
    print("2. 仅启动后端")
    print("3. 仅启动前端")
    print("4. 退出")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    if choice == "1":
        print("\n同时启动前后端服务器...")
        print("按 Ctrl+C 停止所有服务器")
        
        # 在新线程中启动后端
        backend_thread = threading.Thread(target=start_backend_server)
        backend_thread.daemon = True
        backend_thread.start()
        
        # 等待后端启动
        time.sleep(3)
        
        # 启动前端
        start_frontend_server()
        
    elif choice == "2":
        start_backend_server()
    elif choice == "3":
        start_frontend_server()
    elif choice == "4":
        print("退出")
    else:
        print("无效选择")

if __name__ == "__main__":
    main()