from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

# Constants
TICK_SIZE = 0.25

# Enums
class State(Enum):
    ON = 0
    OFF = 1

class SwingDirection(Enum):
    UP = 0
    DOWN = 1
    SIDE_WAY = 2

class DegreeState(Enum):
    TRENDING = 0
    CORRECTION = 1
    OVERBALANCED = 2
    STUCK = 3

class RHYTHM_GEOMETRY(Enum):
    GOLDEN_MEAN = 0
    HARMORNIC = 1
    ARITHMETIC = 2
    OTHER = 3

class XABCD_TYPE(Enum):
    BCD = 0
    ALT1 = 1
    XCD = 2
    XAD = 3
    ALT2 = 4
    RX = 5
    DX = 6

class GeometryType(Enum):
    PIVOT_POINT = 0
    DYNAMIC_RATIO = 1
    CORRECTIONING = 2
    DDRIVE = 3

class TradeState(Enum):
    BUYING = 0
    SELLING = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    NATURAL = 4

# Struct definitions as classes
@dataclass
class Swing:
    high: float = 0.0
    low: float = 0.0
    pre_high: float = 0.0
    pre_low: float = 0.0
    lowIndex: int = 0
    highIndex: int = 0
    size: float = 0.0
    direction: SwingDirection = SwingDirection.SIDE_WAY
    timeHigh: Optional[datetime] = None
    pre_timeHigh: Optional[datetime] = None
    timeLow: Optional[datetime] = None
    pre_timeLow: Optional[datetime] = None

@dataclass
class BRYCLE_STYLE:
    type: XABCD_TYPE = XABCD_TYPE.BCD
    rhythm: RHYTHM_GEOMETRY = RHYTHM_GEOMETRY.OTHER
    price: float = 0.0
    ratio: float = 0.0  # ratio hien tai
    isValid: bool = False
    d_meet: bool = False  # true neu thi truong dat den muc hinh hoc hien tai

@dataclass
class SupportAndResistance:
    type: GeometryType = GeometryType.PIVOT_POINT  # kiểu hình học mục tiêu
    s_rPrice: float = 0.0  # giá mục tiêu hình học
    size: float = 0.0  # kích thước nếu là dạng điều chỉnh
    range: float = 0.0  # phạm vi hình học
    ratio: float = 0.0  # tỷ lệ toán học
    isValid: bool = False  # mức hình học đã dược đạt đến và đã bị vượt qua hay chưa
    direction: SwingDirection = SwingDirection.SIDE_WAY  # xu hướng swing nếu là dạng điều chỉnh
    tradeTicket: int = 0
    tradeState: TradeState = TradeState.NATURAL

# Degree class
@dataclass
class Degree:
    SandR: List[SupportAndResistance] = field(default_factory=list)  # mảng lưu trữ các hỗ trợ kháng cự quan trong
    SandR_count: int = 0  # số hỗ trợ kháng cự được tìm thấy
    swing_size: float = 0.0  # kích thước sóng cho lần đầu tìm kiếm
    correct_swing_size: float = 0.0  # kích thước sóng thật sau khi hoàn tất tìm kiếm
    swings: List[Swing] = field(default_factory=list)  # toàn bộ swing hay các điểm xoay được tìm thấy với kích thước sóng cho trước
    movingSwing: Swing = field(default_factory=Swing)  # swing hiện tại đang di chuyển
    swing_count: int = 0  # tổng số swing được tìm thấy
    direction: SwingDirection = SwingDirection.SIDE_WAY  # hướng của con sóng
    state: DegreeState = DegreeState.STUCK  # trạng thái hiên tại của con sóng có xu hướng trending hoặc đi sideway Stuck v.v....
    timeDegrees: List[datetime] = field(default_factory=list)
    bars: int = 0  # tống số mẫu data series
    legs: int = 0  # number swing that make HH-LL/ LL-HL
    rates_total: int = 0
    
    # Data mẫu
    high: List[float] = field(default_factory=list)
    low: List[float] = field(default_factory=list)
    close: List[float] = field(default_factory=list)
    open: List[float] = field(default_factory=list)
    time: List[datetime] = field(default_factory=list)
    
    # quản lý deals cho con sóng hiện tại
    sumDeals: int = 0
    tradeState: TradeState = TradeState.NATURAL
    deals: List[SupportAndResistance] = field(default_factory=list)
    
    # BRYCLE_STYLE arrays
    BcD: List[BRYCLE_STYLE] = field(default_factory=list)
    Alt1: List[BRYCLE_STYLE] = field(default_factory=list)
    XcD: List[BRYCLE_STYLE] = field(default_factory=list)
    XaD: List[BRYCLE_STYLE] = field(default_factory=list)
    Rx: List[BRYCLE_STYLE] = field(default_factory=list)
    Dx: List[BRYCLE_STYLE] = field(default_factory=list)
    Alt2: List[BRYCLE_STYLE] = field(default_factory=list)
    Ix: List[BRYCLE_STYLE] = field(default_factory=list)
    Ox: List[BRYCLE_STYLE] = field(default_factory=list)

    def updateSwings(self, array):
        """filling the array"""
        if len(array) > 0:
            self.swings = array.copy()
