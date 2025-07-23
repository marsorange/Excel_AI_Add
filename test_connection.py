#!/usr/bin/env python3
"""
测试前后端连接的脚本
"""

import requests
import json
import time

def test_backend_health():
    """测试后端健康状态"""
    print("测试后端连接...")
    
    try:
        # 测试基本连接
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✓ 后端服务器运行正常")
            print("✓ API文档可访问: http://localhost:8000/docs")
            return True
        else:
            print(f"✗ 后端服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ 无法连接到后端服务器 (http://localhost:8000)")
        print("  请确保后端服务器正在运行")
        return False
    except requests.exceptions.Timeout:
        print("✗ 连接后端服务器超时")
        return False
    except Exception as e:
        print(f"✗ 连接后端服务器时出错: {e}")
        return False

def test_cors():
    """测试CORS配置"""
    print("\n测试CORS配置...")
    
    try:
        # 模拟前端的OPTIONS请求
        headers = {
            'Origin': 'https://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type,Authorization'
        }
        
        response = requests.options("http://localhost:8000/register", headers=headers, timeout=5)
        
        if response.status_code in [200, 204]:
            cors_headers = response.headers
            if 'Access-Control-Allow-Origin' in cors_headers:
                print("✓ CORS配置正常")
                print(f"  允许的源: {cors_headers.get('Access-Control-Allow-Origin')}")
                return True
            else:
                print("✗ CORS头部缺失")
                return False
        else:
            print(f"✗ OPTIONS请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"✗ CORS测试失败: {e}")
        return False

def test_api_endpoints():
    """测试API端点"""
    print("\n测试API端点...")
    
    # 测试注册端点
    try:
        test_user = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(
            "http://localhost:8000/register",
            json=test_user,
            timeout=5
        )
        
        if response.status_code in [200, 400]:  # 400可能是用户已存在
            print("✓ 注册端点可访问")
        else:
            print(f"⚠ 注册端点响应异常: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 注册端点测试失败: {e}")
    
    # 测试登录端点
    try:
        login_data = "username=test@example.com&password=testpassword123"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = requests.post(
            "http://localhost:8000/token",
            data=login_data,
            headers=headers,
            timeout=5
        )
        
        if response.status_code in [200, 401]:  # 401可能是用户不存在或密码错误
            print("✓ 登录端点可访问")
        else:
            print(f"⚠ 登录端点响应异常: {response.status_code}")
            
    except Exception as e:
        print(f"✗ 登录端点测试失败: {e}")

def test_frontend_files():
    """测试前端文件是否可访问"""
    print("\n测试前端文件访问...")
    
    frontend_urls = [
        "https://localhost:3000/taskpane.html",
        "https://localhost:3000/assets/icon-32.png"
    ]
    
    for url in frontend_urls:
        try:
            response = requests.get(url, timeout=5, verify=False)  # 忽略SSL证书验证
            if response.status_code == 200:
                print(f"✓ {url} 可访问")
            else:
                print(f"✗ {url} 访问失败: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"✗ 无法连接到 {url}")
            print("  请确保前端服务器正在运行")
        except Exception as e:
            print(f"✗ 访问 {url} 时出错: {e}")

def main():
    """主函数"""
    print("=== Excel AI 助手连接测试 ===")
    
    # 测试后端
    backend_ok = test_backend_health()
    
    if backend_ok:
        test_cors()
        test_api_endpoints()
    
    # 测试前端
    test_frontend_files()
    
    print("\n=== 测试完成 ===")
    
    if backend_ok:
        print("\n✅ 后端测试通过")
        print("📖 API文档: http://localhost:8000/docs")
    else:
        print("\n❌ 后端测试失败")
        print("💡 请运行: python start_backend.py")
    
    print("\n💡 前端启动命令: ./start_frontend.sh 或 npm run dev-server")
    print("🌐 前端地址: https://localhost:3000")

if __name__ == "__main__":
    main()