#!/usr/bin/env python3
"""
快速启动脚本 - 用于测试系统是否正常工作
"""

import sys
import requests


def check_ollama():
    """检查 Ollama 是否运行"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("✅ Ollama 运行正常")
            if models:
                print(f"   可用模型: {', '.join([m['name'] for m in models])}")
            else:
                print("   ⚠️  未找到已安装的模型，请运行: ollama pull llama3.2")
            return True
        else:
            print("❌ Ollama 响应异常")
            return False
    except Exception as e:
        print(f"❌ 无法连接到 Ollama (http://localhost:11434)")
        print(f"   错误: {e}")
        print(f"   请确保 Ollama 已安装并运行: ollama serve")
        return False


def check_dependencies():
    """检查依赖是否安装"""
    required = ['arxiv', 'yaml', 'requests']
    missing = []

    for module in required:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)

    if missing:
        print(f"❌ 缺少依赖包: {', '.join(missing)}")
        print(f"   请运行: pip install -r requirements.txt")
        return False
    else:
        print("✅ 所有依赖已安装")
        return True


def check_config():
    """检查配置文件"""
    import os
    if os.path.exists('config.yaml'):
        print("✅ 配置文件存在")
        return True
    else:
        print("⚠️  配置文件不存在，将使用默认配置")
        return True


def main():
    print("=" * 60)
    print("arXiv 研究助手 - 系统检查")
    print("=" * 60)

    checks = [
        ("依赖检查", check_dependencies),
        ("配置检查", check_config),
        ("Ollama 检查", check_ollama),
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\n{name}:")
        if not check_func():
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有检查通过！可以运行: python main.py")
    else:
        print("❌ 部分检查失败，请根据上述提示解决问题")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
