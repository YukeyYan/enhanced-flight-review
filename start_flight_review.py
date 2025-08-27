#!/usr/bin/env python3
"""
Flight Review 启动脚本
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """检查依赖项"""
    required_packages = [
        'bokeh', 'jinja2', 'pyulog', 'requests', 'scipy', 'simplekml'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ 缺少依赖包:")
        for package in missing_packages:
            print(f"   - {package}")
        return False
    
    return True

def check_config():
    """检查配置文件"""
    config_file = "app/config_user.ini" if os.path.exists("app/config_user.ini") else "config_user.ini"
    
    if not os.path.exists(config_file):
        print("❌ 配置文件不存在: config_user.ini")
        return False
    
    # 检查API密钥
    with open(config_file, 'r') as f:
        content = f.read()
        if 'cesium_api_key =' in content and 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' in content:
            print("✅ Cesium API密钥已配置")
            return True
        else:
            print("❌ Cesium API密钥未配置")
            return False

def main():
    """主函数"""
    print("🚁 Flight Review 启动器")
    print("=" * 40)
    
    # 检查依赖项
    print("🔍 检查依赖项...")
    if not check_dependencies():
        print("\n💡 安装缺少的依赖项:")
        print("   pip install bokeh jinja2 pyulog requests scipy simplekml")
        return False
    
    print("✅ 依赖项检查通过")
    
    # 检查配置
    print("🔍 检查配置...")
    if not check_config():
        return False
    
    print("✅ 配置检查通过")
    
    # 启动服务器
    print("\n🚀 启动 Flight Review 服务器...")
    print("📍 地址: http://localhost:5006")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 40)
    
    try:
        # 启动服务器
        serve_script = "app/serve.py" if os.path.exists("app/serve.py") else "serve.py"
        cmd = [sys.executable, serve_script, "--port", "5006", "--host", "localhost"]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 等待服务器启动
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ Flight Review 服务器已启动!")
            print("🌐 访问: http://localhost:5006")
            
            # 实时显示输出
            try:
                for line in process.stdout:
                    print(line.strip())
            except KeyboardInterrupt:
                print("\n🛑 正在停止服务器...")
                process.terminate()
                process.wait()
                print("✅ 服务器已停止")
        else:
            print("❌ 服务器启动失败")
            output, _ = process.communicate()
            if output:
                print("错误输出:")
                print(output)
            return False
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断")
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
