"""
本地测试脚本：检查解析函数助教的环境配置
运行方式：python test_local.py
"""
import sys
import subprocess

def check_python():
    print(f"🐍 Python 版本: {sys.version}")
    print(f"   Python 路径: {sys.executable}")
    print()

def check_module(name, install_cmd=None):
    try:
        __import__(name)
        print(f"  ✅ {name} 已安装")
        return True
    except ImportError:
        print(f"  ❌ {name} 未安装")
        if install_cmd:
            print(f"     安装命令: {install_cmd}")
        return False

def check_app_syntax():
    app_path = r"D:\AI\Sample\解析函数\deploy\app.py"
    print(f"\n📄 检查 app.py 语法...")
    print(f"   文件路径: {app_path}")
    
    try:
        with open(app_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        compile(code, app_path, "exec")
        print("  ✅ app.py 语法正确！")
        
        # 检查关键内容
        keywords = ["概念定位", "核心公式", "详细推导", "物理直觉", "常见错误", "自检提问"]
        print(f"\n📋 检查系统提示词完整性:")
        for kw in keywords:
            status = "✅" if kw in code else "❌"
            print(f"     {status} {kw}")
        
        return True
    except SyntaxError as e:
        print(f"  ❌ 语法错误: {e}")
        return False
    except FileNotFoundError:
        print(f"  ❌ 文件未找到: {app_path}")
        return False

def main():
    print("=" * 60)
    print("📐 解析函数助教 - 本地环境测试")
    print("=" * 60)
    
    check_python()
    
    print("📦 检查依赖包...")
    all_ok = True
    all_ok &= check_module("streamlit", "pip install streamlit")
    all_ok &= check_module("requests", "pip install requests")
    
    syntax_ok = check_app_syntax()
    
    print("\n" + "=" * 60)
    if all_ok and syntax_ok:
        print("🎉 测试通过！可以运行本地服务了。")
        print("=" * 60)
        print("\n启动命令:")
        print(r'  cd "D:\AI\Sample\解析函数\deploy"')
        print(r'  streamlit run app.py')
        print("\n然后在浏览器中打开:")
        print("  http://localhost:8501")
    else:
        print("⚠️ 测试未通过，请按以下步骤修复:")
        print("=" * 60)
        if not all_ok:
            print("\n1. 安装缺失的依赖包:")
            print("   pip install streamlit requests")
        if not syntax_ok:
            print("\n2. 检查 app.py 文件是否存在且内容正确")
    
    print()
    input("按 Enter 键退出...")

if __name__ == "__main__":
    main()
