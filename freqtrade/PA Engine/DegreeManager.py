from typing import List, Optional, Dict, Any
import math
from datetime import datetime
from .Type import Swing, SwingDirection, Degree, DegreeState, TradeState, TICK_SIZE
from .SwingFactory import SwingFactory
from .Geometry import GeometryManager

class DegreeManager:
    """Python implementation of the DegreeManger class from MQL5"""
    
    def __init__(self, symbol_name: str = ""):
        self.degrees: List[Degree] = []
        self.symbol_name: str = symbol_name
        self.degree_count: int = 0
    
    @staticmethod
    def direction(degree: Degree) -> SwingDirection:
        """Determine the direction of a degree based on its swings"""
        # Default degree direction
        degree_direction = SwingDirection.SIDE_WAY
        degree.direction = SwingDirection.SIDE_WAY
        degree.state = DegreeState.STUCK
        degree.legs = 3
        
        # Reject if not enough swing in degree
        if degree.swing_count < 4:
            degree.legs = 3
            return SwingDirection.SIDE_WAY
        
        # Init direction degree by 4 first swings
        swing1 = degree.swings[degree.swing_count - 1]
        swing2 = degree.swings[degree.swing_count - 2]
        swing3 = degree.swings[degree.swing_count - 3]
        swing4 = degree.swings[degree.swing_count - 4]
        degree.correct_swing_size = swing1.size
        
        if swing1.direction == SwingDirection.UP:
            # Swing 1 tăng trong 1 xu hướng tăng (đang phát triển sóng tăng)
            if swing1.high > swing3.high and swing2.low > swing4.low:
                degree_direction = SwingDirection.UP
                degree.state = DegreeState.TRENDING
                # ghi nhận lại cho đúng kích thước thật con sóng
                # vì con sóng hiện tại đang phát triển nên kích thước thật con sóng là đợt điều chỉnh thứ 1
                degree.correct_swing_size = swing2.size
            
            # Swing 1 tằng Trong xu hướng giảm(tăng điều chỉnh)
            elif degree.swing_count > 4:
                swing5 = degree.swings[degree.swing_count - 5]
                if swing1.high < swing3.high and swing3.high < swing5.high and swing2.low < swing4.low:
                    degree_direction = SwingDirection.DOWN
                    # Xác định xem đợt điều chỉnh này đã làm mất cân bằng hay chưa
                    if not SwingFactory.value_is_in_tick_range(swing1.size, swing3.size):
                        # đợt hiệu chỉnh đã làm mất cân bằng con sóng
                        degree.state = DegreeState.OVERBALANCED
                    else:
                        degree.state = DegreeState.CORRECTION
                    # ghi nhận lại cho đúng kích thước thật con sóng
                    # vì con sóng hiện tại đang điều chỉnh nên kích thước thật con sóng là đợt điều chỉnh thứ 2
                    degree.correct_swing_size = swing3.size
        
        elif swing1.direction == SwingDirection.DOWN:
            # Swing 1 giảm trong 1 xu hướng giảm (phát triển sóng giảm)
            if swing2.high < swing4.high and swing1.low < swing3.low:
                degree_direction = SwingDirection.DOWN
                degree.state = DegreeState.TRENDING
                # ghi nhận lại cho đúng kích thước thật con sóng
                # vì con sóng hiện tại đang phát triển nên kích thước thật con sóng là đợt điều chỉnh thứ 1
                degree.correct_swing_size = swing2.size
            
            # Swing 1 giảm trong 1 xu hướng tăng (giảm điều chỉnh)
            elif degree.swing_count > 4:
                swing5 = degree.swings[degree.swing_count - 5]
                if swing2.high > swing4.high and swing1.low > swing3.low and swing3.low > swing5.low:
                    degree_direction = SwingDirection.UP
                    # Xác định xem đợt điều chỉnh này đã làm mất cân bằng hay chưa
                    if not SwingFactory.value_is_in_tick_range(swing1.size, swing3.size):
                        # đợt hiệu chỉnh đã làm mất cân bằng con sóng
                        degree.state = DegreeState.OVERBALANCED
                    else:
                        degree.state = DegreeState.CORRECTION
                    # ghi nhận lại cho đúng kích thước thật con sóng
                    # vì con sóng hiện tại đang điều chỉnh nên kích thước thật con sóng là đợt điều chỉnh thứ 2
                    degree.correct_swing_size = swing3.size
        
        # No trend found
        if degree_direction == SwingDirection.SIDE_WAY:
            degree.legs = 5
            degree.state = DegreeState.STUCK
            return degree_direction
        
        if degree.state == DegreeState.OVERBALANCED:
            degree.legs = 5
            return degree_direction
        
        # Check additional legs in wave
        for index in range(degree.swing_count - 4, 1, -1):
            current_swing = degree.swings[index]
            swing_shift2 = degree.swings[index + 2]
            
            if degree_direction == SwingDirection.UP:
                # In an upward wave the next wave legs must satisfy:
                # UP: This up leg must not be higher than the previous up leg
                if current_swing.direction == SwingDirection.UP and current_swing.high <= swing_shift2.high:
                    # If conditions met, wave has one more up leg
                    degree.legs += 1
                    continue
                
                # DOWN: This down leg must not be lower than the previous down leg
                # This price drop does not exceed the current wave correction size
                if current_swing.direction == SwingDirection.DOWN and current_swing.low <= swing_shift2.low:
                    # If conditions met, wave has one more down leg
                    degree.legs += 1
                    continue
            
            elif degree_direction == SwingDirection.DOWN:
                # In a downward wave the next wave legs must satisfy:
                # UP: This up leg must be higher than the previous up leg
                # This corrective rise does not exceed the current wave correction size
                if current_swing.direction == SwingDirection.UP and current_swing.high >= swing_shift2.high:
                    # If conditions met, wave has one more up leg
                    degree.legs += 1
                    continue
                
                # DOWN: This down leg must be lower than the previous down leg
                if current_swing.direction == SwingDirection.DOWN and current_swing.low >= swing_shift2.low:
                    # If conditions met, wave has one more down leg
                    degree.legs += 1
                    continue
            
            # No more legs found that belong to current wave, exit loop
            break
        
        if degree.swing_count > 4 and degree.legs == 4:
            degree.legs = 5
            return degree_direction
        
        if degree.legs > 5:
            # If last leg matches degree direction in a trending market, remove that leg
            if (degree_direction == SwingDirection.UP and 
                degree.swings[degree.swing_count - degree.legs].direction == SwingDirection.UP):
                degree.legs -= 1
            
            if (degree_direction == SwingDirection.DOWN and 
                degree.swings[degree.swing_count - degree.legs].direction == SwingDirection.DOWN):
                degree.legs -= 1
        
        return degree_direction
    
    @staticmethod
    def is_valid_degree(degree: Degree, directions: List[SwingDirection]) -> bool:
        """Check if a degree is valid based on a list of directions"""
        is_valid_degree = True
        for direction in directions:
            if degree.direction == direction:
                is_valid_degree = False
                return is_valid_degree
        return is_valid_degree
    
    def filter_degree_with(self, directions: List[SwingDirection]) -> float:
        """Filter degrees that match specified directions"""
        start = 0
        first_degree_removed = 0.0
        
        while start < self.degree_count and self.degree_count > 0:
            current_degree = self.degrees[start]
            if not DegreeManager.is_valid_degree(current_degree, directions):
                if first_degree_removed == 0:
                    first_degree_removed = current_degree.swing_size
                
                # Remove the degree at index 'start'
                self.degrees.pop(start)
                self.degree_count -= 1
                start = 0
                continue
            
            start += 1
        
        return first_degree_removed
    
    def minimum_swing_size(self, degree: Degree) -> None:
        """Calculate the minimum swing size for a degree"""
        direction = self.direction(degree)
        minimum_swing_found = 0.0
        
        if direction != SwingDirection.SIDE_WAY:
            swing = degree.swings[1]
            minimum_swing_found = swing.size
            degree.swing_size = minimum_swing_found
    
    def is_duplicated(self, degree: Degree, degrees: List[Degree]) -> bool:
        """Check if a degree is duplicated in the given list"""
        for start in range(self.degree_count):
            compare_d = degrees[start]
            sum_swing_duplicated = 0
            
            for i in range(1, degree.legs + 1):
                if compare_d.swings[compare_d.swing_count - i].direction != degree.swings[degree.swing_count - i].direction:
                    break
                
                if (compare_d.swings[compare_d.swing_count - i].high == degree.swings[degree.swing_count - i].high or 
                    compare_d.swings[compare_d.swing_count - i].low == degree.swings[degree.swing_count - i].low):
                    sum_swing_duplicated += 1
            
            if sum_swing_duplicated == degree.legs:
                return True
        
        return False
    
    def find_all_degree_from(self, rates_total: int,
                             time: List[datetime],
                             open_prices: List[float],
                             high_prices: List[float],
                             low_prices: List[float],
                             close_prices: List[float],
                             minimum_swing_size: float) -> int:
        """Find all degrees from price data with specified minimum swing size"""
        degree = Degree()
        is_update_degree = False
        degree_tmp = []
        
        if self.degree_count > 0:
            if (round(minimum_swing_size, 2) == round(self.degrees[0].swing_size, 2) or 
                minimum_swing_size == 0.0):
                return self.degree_count
            
            degree = self.degrees[0]
            is_update_degree = True
            degree_tmp = self.degrees.copy()
        
        tick_size = SwingFactory.get_current_tick_size()
        count = 0
        min_size = minimum_swing_size
        max_size = 50.0
        
        # Get the size of the first bar (simple approximation for Python version)
        first_bar_size = abs(high_prices[1] - low_prices[1]) if len(high_prices) > 1 and len(low_prices) > 1 else 2.0
        
        for start in [x * tick_size + max(2.0, first_bar_size) for x in range(int((max_size - max(2.0, first_bar_size)) / tick_size) + 1)]:
            # Break if we're above the maximum or above the current degree swing size when updating
            if start > max_size or (is_update_degree and start > degree.swing_size):
                break
            
            current_degree = Degree()
            SwingFactory.get_all_swing_from(current_degree, rates_total, time, open_prices, high_prices, low_prices, close_prices, start)
            
            # If swing count < 5, break loop
            if current_degree.swing_count < 5:
                break
            
            current_degree.direction = self.direction(current_degree)
            
            if self.is_duplicated(current_degree, self.degrees):
                continue
            
            # Capture current context
            current_degree.rates_total = rates_total
            current_degree.tradeState = TradeState.NATURAL
            current_degree.sumDeals = 0
            
            # Call GeometryManager methods
            GeometryManager.detect_support_and_resistance_for(current_degree)
            GeometryManager.detect_brycle_xabcd(current_degree)
            
            if is_update_degree:
                self.degrees.insert(0, current_degree)
                self.degree_count += 1
            else:
                self.degrees.append(current_degree)
                self.degree_count += 1
            
            count += 1
        
        return count