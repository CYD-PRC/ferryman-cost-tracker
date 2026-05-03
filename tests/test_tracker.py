#!/usr/bin/env python3
"""
基础测试（占位）

运行：python -m pytest tests/
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_import():
    """测试基本导入"""
    from tracker import FerrymanTracker
    from router import gear_aware_call, MODEL_REGISTRY
    assert FerrymanTracker is not None
    assert gear_aware_call is not None
    assert len(MODEL_REGISTRY) == 4
    print("✓ 导入测试通过")


def test_pricing():
    """测试价格计算"""
    from tracker import PRICING
    assert "deepseek" in PRICING
    assert "qwen" in PRICING
    assert "kimi" in PRICING
    print("✓ 价格配置测试通过")


def test_gear_entropy():
    """测试档位熵值映射"""
    from tracker import GEAR_ENTROPY_MAP
    assert GEAR_ENTROPY_MAP[1] == 0.0
    assert GEAR_ENTROPY_MAP[2] == 0.25
    assert GEAR_ENTROPY_MAP[3] == 0.75
    assert GEAR_ENTROPY_MAP[4] == 1.5
    print("✓ 熵值映射测试通过")


if __name__ == "__main__":
    test_import()
    test_pricing()
    test_gear_entropy()
    print("\n所有测试通过 ✓")
