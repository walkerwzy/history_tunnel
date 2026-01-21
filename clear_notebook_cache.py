#!/usr/bin/env python3
"""
清理Jupyter Notebook缓存和重新加载模块的工具
"""

import sys
import importlib
import gc
from types import ModuleType

def clear_module_cache():
    """清除Python模块缓存"""
    print("🧹 清除Python模块缓存...")

    # 清除特定模块的缓存
    modules_to_clear = [
        'timeline_generator',
        'langchain_processor',
        'wikipedia_scraper',
        'database_manager',
        'langchain_community',
        'langchain_core'
    ]

    for module_name in modules_to_clear:
        if module_name in sys.modules:
            try:
                # 重新加载模块
                importlib.reload(sys.modules[module_name])
                print(f"  ✅ 重新加载: {module_name}")
            except Exception as e:
                print(f"  ❌ 重新加载失败 {module_name}: {e}")

    # 强制垃圾回收
    gc.collect()
    print("  ✅ 垃圾回收完成")

def restart_imports():
    """重新导入所有模块"""
    print("\n🔄 重新导入模块...")

    try:
        # 清除sys.modules中的相关模块
        modules_to_remove = [
            'timeline_generator',
            'langchain_processor',
            'wikipedia_scraper',
            'database_manager'
        ]

        for module in modules_to_remove:
            if module in sys.modules:
                del sys.modules[module]
                print(f"  ✅ 移除缓存: {module}")

        # 重新导入
        from timeline_generator import TimelineGenerator
        from langchain_processor import HistoricalDataProcessor
        from wikipedia_scraper import WikipediaScraper

        print("  ✅ 重新导入成功")

        # 测试初始化
        print("\n🧪 测试初始化...")
        generator = TimelineGenerator(region="Chinese")
        print(f"  ✅ TimelineGenerator: has_processor={generator.has_processor}")

        return True

    except Exception as e:
        print(f"  ❌ 重新导入失败: {e}")
        return False

def clear_jupyter_cache():
    """提供Jupyter缓存清理命令"""
    print("\n📋 Jupyter Notebook缓存清理指南:")
    print("=" * 50)
    print("方法1: 重启内核")
    print("  在Jupyter菜单: Kernel -> Restart Kernel")
    print("  或: Ctrl/Cmd + .")
    print()
    print("方法2: 重启并清除输出")
    print("  在Jupyter菜单: Kernel -> Restart & Clear Output")
    print()
    print("方法3: 重启并运行所有")
    print("  在Jupyter菜单: Kernel -> Restart & Run All")
    print()
    print("方法4: 清除cell输出")
    print("  在Jupyter菜单: Cell -> All Output -> Clear")
    print()
    print("方法5: 命令行清理（如果适用）")
    print("  jupyter nbconvert --clear-output your_notebook.ipynb")
    print("  或删除 .ipynb_checkpoints/ 目录")
    print()
    print("方法6: 浏览器缓存清理")
    print("  硬刷新页面: Ctrl/Cmd + Shift + R")
    print("  或清除浏览器缓存")

if __name__ == "__main__":
    print("🧹 Jupyter Notebook缓存清理工具")
    print("=" * 50)

    # 清除Python缓存
    clear_module_cache()

    # 重新导入
    success = restart_imports()

    # 显示清理指南
    clear_jupyter_cache()

    print("\n" + "=" * 50)
    if success:
        print("✅ 缓存清理完成！建议在notebook中：")
        print("   1. 重启内核 (Kernel -> Restart)")
        print("   2. 重新运行所有cell (Cell -> Run All)")
    else:
        print("❌ 缓存清理遇到问题，请手动重启Jupyter内核")