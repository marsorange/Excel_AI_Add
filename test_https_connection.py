#!/usr/bin/env python3
"""
测试 HTTPS 连接的脚本
验证前后端 HTTPS 配置是否正常工作
"""

import requests
import ssl
import socket
import subprocess
import sys
import time
from urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告（仅用于开发环境测试）
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_backend_https():
    """测试后端 HTTPS 服务"""
    print("🔒 测试后端 HTTPS 服务...")
    
    try:
        # 测试 HTTPS 连接
        response = requests.get(
            "https://localhost:8000/docs", 
            timeout=10,
            verify=False  # 忽略自签名证书验证
        )
        
        if response.status_code == 200:
            print("✅ 后端 HTTPS 服务运行正常")
            print("📚 API 文档: https://localhost:8000/docs")
            return True
        else:
            print(f"❌ 后端 HTTPS 服务响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.SSLError as e:
        print(f"🔐 SSL 错误: {e}")
        print("💡 这可能是证书问题，但服务可能仍在运行")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端 HTTPS 服务 (https://localhost:8000)")
        print("💡 请确保后端服务器正在运行并支持 HTTPS")
        return False
    except Exception as e:
        print(f"❌ 连接后端 HTTPS 服务时出错: {e}")
        return False

def test_frontend_https():
    """测试前端 HTTPS 服务"""
    print("\n🌐 测试前端 HTTPS 服务...")
    
    try:
        response = requests.get(
            "https://localhost:3000/taskpane.html", 
            timeout=10,
            verify=False
        )
        
        if response.status_code == 200:
            print("✅ 前端 HTTPS 服务运行正常")
            print("🖥️  访问地址: https://localhost:3000")
            return True
        else:
            print(f"❌ 前端 HTTPS 服务响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到前端 HTTPS 服务 (https://localhost:3000)")
        print("💡 请确保前端服务器正在运行")
        return False
    except Exception as e:
        print(f"❌ 连接前端 HTTPS 服务时出错: {e}")
        return False

def test_api_endpoints():
    """测试 API 端点的 HTTPS 连接"""
    print("\n🔗 测试 API 端点...")
    
    # 测试注册端点
    try:
        test_user = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        response = requests.post(
            "https://localhost:8000/register",
            json=test_user,
            timeout=10,
            verify=False
        )
        
        if response.status_code in [200, 400]:  # 400可能是用户已存在
            print("✅ 注册端点 HTTPS 可访问")
        else:
            print(f"⚠️  注册端点响应异常: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 注册端点测试失败: {e}")

def check_certificates():
    """检查证书配置"""
    print("\n📜 检查证书配置...")
    
    # 检查后端证书
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection(("localhost", 8000), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname="localhost") as ssock:
                print("✅ 后端 SSL 证书配置正常")
                cert = ssock.getpeercert()
                if cert:
                    print(f"📄 证书主题: {cert.get('subject', 'N/A')}")
                    print(f"📅 证书有效期: {cert.get('notAfter', 'N/A')}")
    except Exception as e:
        print(f"❌ 后端 SSL 证书检查失败: {e}")

def main():
    """主函数"""
    print("🚀 Excel AI 助手 - HTTPS 连接测试")
    print("=" * 50)
    
    # 测试后端
    backend_ok = test_backend_https()
    
    # 测试前端
    frontend_ok = test_frontend_https()
    
    # 测试 API 端点
    if backend_ok:
        test_api_endpoints()
    
    # 检查证书
    check_certificates()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    if backend_ok:
        print("✅ 后端 HTTPS: 正常")
    else:
        print("❌ 后端 HTTPS: 异常")
    
    if frontend_ok:
        print("✅ 前端 HTTPS: 正常")
    else:
        print("❌ 前端 HTTPS: 异常")
    
    if backend_ok and frontend_ok:
        print("\n🎉 所有 HTTPS 服务运行正常！")
        print("💡 现在可以在 Excel 中正常使用插件了")
    else:
        print("\n⚠️  部分服务异常，请检查服务是否启动")
        print("💡 启动命令:")
        print("   前端: npm run dev-server")
        print("   后端: cd backend && python main.py")

if __name__ == "__main__":
    main() 