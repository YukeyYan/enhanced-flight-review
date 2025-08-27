#!/usr/bin/env python3
"""
GitHub 自动上传脚本
Enhanced Flight Review Project
"""

import os
import sys
import subprocess
import webbrowser
from urllib.parse import quote

def run_command(cmd, description=""):
    """运行命令并显示结果"""
    print(f"🔄 {description}")
    print(f"   命令: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ 成功!")
            if result.stdout.strip():
                print(f"   输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ 失败!")
            if result.stderr.strip():
                print(f"   错误: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return False

def check_git_config():
    """检查 Git 配置"""
    print("🔍 检查 Git 配置...")
    
    # 检查用户名
    result = subprocess.run("git config user.name", shell=True, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print("⚠️  Git 用户名未配置")
        name = input("请输入您的 Git 用户名: ")
        run_command(f'git config user.name "{name}"', "设置 Git 用户名")
    else:
        print(f"✅ Git 用户名: {result.stdout.strip()}")
    
    # 检查邮箱
    result = subprocess.run("git config user.email", shell=True, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        print("⚠️  Git 邮箱未配置")
        email = input("请输入您的 Git 邮箱: ")
        run_command(f'git config user.email "{email}"', "设置 Git 邮箱")
    else:
        print(f"✅ Git 邮箱: {result.stdout.strip()}")

def create_github_repo():
    """指导创建 GitHub 仓库"""
    print("\n🌐 创建 GitHub 仓库")
    print("=" * 50)
    
    repo_name = "enhanced-flight-review"
    description = "🚁 专业无人机飞行日志分析系统 - Enhanced PX4 Flight Review with 3D visualization and intelligent analysis"
    
    print("请按照以下步骤在 GitHub 创建仓库:")
    print("\n1. 🌐 打开 GitHub 网站")
    print("   我将为您自动打开 GitHub 新建仓库页面...")
    
    # 构建 GitHub 新建仓库的 URL
    github_url = f"https://github.com/new?name={quote(repo_name)}&description={quote(description)}"
    
    try:
        webbrowser.open(github_url)
        print("✅ 已在浏览器中打开 GitHub")
    except:
        print(f"❌ 无法自动打开浏览器，请手动访问: {github_url}")
    
    print(f"\n2. 📝 填写仓库信息:")
    print(f"   Repository name: {repo_name}")
    print(f"   Description: {description}")
    print(f"   Visibility: Public (推荐)")
    print(f"   ❌ 不要勾选 'Add a README file'")
    print(f"   ❌ 不要勾选 'Add .gitignore'")
    print(f"   ❌ 不要勾选 'Choose a license'")
    
    print(f"\n3. 🚀 点击 'Create repository' 按钮")
    
    input("\n按 Enter 键继续 (确认您已创建了 GitHub 仓库)...")
    
    return repo_name

def get_github_username():
    """获取 GitHub 用户名"""
    print("\n👤 GitHub 用户名")
    print("=" * 30)
    
    username = input("请输入您的 GitHub 用户名: ").strip()
    
    if not username:
        print("❌ 用户名不能为空!")
        return get_github_username()
    
    return username

def upload_to_github():
    """上传到 GitHub"""
    print("\n🚀 上传到 GitHub")
    print("=" * 30)
    
    username = get_github_username()
    repo_name = "enhanced-flight-review"
    
    remote_url = f"https://github.com/{username}/{repo_name}.git"
    
    print(f"📍 远程仓库地址: {remote_url}")
    
    # 添加远程仓库
    if not run_command(f"git remote add origin {remote_url}", "添加远程仓库"):
        # 如果已存在，尝试更新
        run_command(f"git remote set-url origin {remote_url}", "更新远程仓库地址")
    
    # 推送到 GitHub
    print("\n🔄 推送到 GitHub...")
    print("⚠️  如果是第一次推送，可能需要输入 GitHub 用户名和密码/Token")
    
    if run_command("git push -u origin main", "推送到 GitHub"):
        print("\n🎉 上传成功!")
        
        # 打开 GitHub 仓库页面
        repo_url = f"https://github.com/{username}/{repo_name}"
        print(f"🌐 仓库地址: {repo_url}")
        
        try:
            webbrowser.open(repo_url)
            print("✅ 已在浏览器中打开您的仓库")
        except:
            print(f"❌ 无法自动打开浏览器，请手动访问: {repo_url}")
        
        return True
    else:
        print("\n❌ 上传失败!")
        print("\n💡 可能的解决方案:")
        print("1. 检查网络连接")
        print("2. 确认 GitHub 用户名正确")
        print("3. 检查 GitHub 仓库是否已创建")
        print("4. 确认 Git 凭据配置正确")
        return False

def main():
    """主函数"""
    print("🚁 Enhanced Flight Review - GitHub 上传工具")
    print("=" * 60)
    
    # 检查是否在正确的目录
    if not os.path.exists("app/serve.py"):
        print("❌ 请在 flight_review_clean 目录中运行此脚本!")
        sys.exit(1)
    
    print("✅ 项目目录检查通过")
    
    # 检查 Git 状态
    print("\n🔍 检查项目状态...")
    
    if not os.path.exists(".git"):
        print("❌ Git 仓库未初始化!")
        sys.exit(1)
    
    print("✅ Git 仓库已初始化")
    
    # 检查 Git 配置
    check_git_config()
    
    # 检查是否有未提交的更改
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("\n⚠️  发现未提交的更改:")
        print(result.stdout)
        
        if input("是否提交这些更改? (y/n): ").lower() == 'y':
            run_command("git add .", "添加所有更改")
            commit_msg = input("请输入提交信息 (按 Enter 使用默认信息): ").strip()
            if not commit_msg:
                commit_msg = "📤 准备上传到 GitHub"
            run_command(f'git commit -m "{commit_msg}"', "提交更改")
    
    print("\n✅ 项目准备完成!")
    
    # 创建 GitHub 仓库指导
    repo_name = create_github_repo()
    
    # 上传到 GitHub
    if upload_to_github():
        print("\n🎉 恭喜! 项目已成功上传到 GitHub!")
        print("\n📋 接下来您可以:")
        print("1. 🏷️  创建第一个 Release 版本")
        print("2. 🎨 添加项目主题标签")
        print("3. 📚 启用 GitHub Pages (可选)")
        print("4. 🤝 邀请其他开发者协作")
        
        print(f"\n🌟 您的项目: https://github.com/{get_github_username()}/{repo_name}")
    else:
        print("\n❌ 上传失败，请检查错误信息并重试")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)
