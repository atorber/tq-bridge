#!/usr/bin/env python3
"""检查 tq_bridge 网关健康状态。"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from call import cmd_health  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(cmd_health())
