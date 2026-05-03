#!/usr/bin/env python3
"""
基础用法示例

运行前确保设置环境变量：
export DEEPSEEK_API_KEY=your_key_here
export BAILIAN_API_KEY=your_key_here
export KIMI_API_KEY=your_key_here
"""

import os
import sys

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tracker import FerrymanTracker


def main():
    # 初始化追踪器
    tracker = FerrymanTracker(
        department="engineering",
        log_file="demo_cost_log.jsonl"
    )
    
    print("=" * 50)
    print("Ferryman Cost Tracker - 基础演示")
    print("=" * 50)
    
    # 不同档位的调用示例
    test_messages = [
        (1, "1+1 等于几？"),           # EMBRACE - 简单问题
        (2, "今晚吃什么？"),           # EXPLORE - 需要建议
        (3, "解释一下量子纠缠"),       # ADAPT - 需要详细解释
        (4, "写一首关于春天的诗"),     # LET_GO - 自由创作
    ]
    
    for gear, message in test_messages:
        print(f"\n[档位 {gear}] {message}")
        print("-" * 40)
        
        result = tracker.chat(
            message=message,
            model_id="deepseek",  # 可改为 qwen/kimi
            gear=gear
        )
        
        if result.get("success"):
            print(f"回复：{result.get('reply', '')[:100]}...")
            print(f"成本：${result.get('cost_usd', 0):.6f}")
            print(f"Token: 输入{result.get('tokens', {}).get('input', 0)} / 输出{result.get('tokens', {}).get('output', 0)}")
            print(f"延迟：{result.get('latency_ms', 0):.0f}ms")
        else:
            print(f"错误：{result.get('error', '未知错误')}")
    
    # 获取报告
    print("\n" + "=" * 50)
    print("成本报告")
    print("=" * 50)
    
    report = tracker.get_report()
    print(f"总调用次数：{report['total_calls']}")
    print(f"总成本：${report['total_cost_usd']:.4f}")
    print(f"平均熵值：{report['avg_entropy']:.3f}")
    print(f"\n按档位统计：{report['by_gear']}")
    print(f"按模型统计：{report['by_model']}")


if __name__ == "__main__":
    main()
