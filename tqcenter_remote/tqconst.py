"""与官方 tqcenter.tqconst 保持一致的常量定义（纯本地，无网络）。"""


class ConstMeta(type):
    def __setattr__(cls, name, value):
        raise AttributeError(f"不能修改类常量 {name}")


class tqconst(metaclass=ConstMeta):
    STOCK_BUY = 0
    STOCK_SELL = 1

    CREDIT_BUY = 0
    CREDIT_SELL = 1

    CREDIT_FIN_BUY = 69
    CREDIT_SLO_SELL = 70

    CREDIT_COV_BUY = 71
    CREDIT_STK_REPAY = 76

    ETF_PURCHASE = 45
    ETF_REDEMPTION = 46

    FUTURE_OPEN_LONG = 101
    FUTURE_OPEN_SHORT = 102
    FUTURE_CLOSE_LONG = 103
    FUTURE_CLOSE_SHORT = 104

    OPTION_OPEN_LONG = 201
    OPTION_OPEN_SHORT = 202
    OPTION_CLOSE_LONG = 203
    OPTION_CLOSE_SHORT = 204

    PRICE_MY = 0
    PRICE_SJ = 1
    PRICE_ZTJ = 2
    PRICE_DTJ = 3

    WTSTATUS_NULL = 0
    WTSTATUS_NOCJ = 1
    WTSTATUS_PARTCJ = 2
    WTSTATUS_ALLCJ = 3
    WTSTATUS_BCBC = 4
    WTSTATUS_ALLCD = 5

    def __setattr__(self, name, value):
        raise AttributeError(f"不能修改常量 {name}")
