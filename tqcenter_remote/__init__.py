"""
跨平台 tqcenter 远程兼容 SDK（Windows / macOS / Linux）。

通过 tq_bridge 网关调用本机通达信，业务代码仅改包名：
    from tqcenter_remote import tq, tqconst
    tq.initialize(__file__)
"""

from .client import tq
from .tqconst import tqconst

__all__ = ["tq", "tqconst"]
__version__ = "1.0.0"
