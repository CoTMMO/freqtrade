from typing import List, Optional, Tuple
from datetime import datetime
import math
from .Type import Swing, SwingDirection, Degree, TICK_SIZE, DegreeState, TradeState
from .Geometry import GeometryManager

class SwingFactory:
    """Implementation of the Swingfactory class from MQL5"""
    
    @staticmethod
    def get_price_from_swing(swing: Swing) -> float:
        """Get the price from a swing based on its direction"""
        if swing.direction == SwingDirection.UP:
            return swing.high
        else:
            return swing.low
    
    @staticmethod
    def value_is_valid_with_tick_range(value1: float, value2: float) -> bool:
        """Check if value1 is valid within tick range of value2"""
        if value1 >= value2:
            return True
        if value1 >= (value2 - SwingFactory.get_current_tick_size()):
            return True
        return False
    
    @staticmethod
    def value_is_in_tick_range(value1: float, value2: float) -> bool:
        """Check if value1 is in tick range of value2"""
        if value1 <= value2:
            return True
        if value1 >= (value2 - SwingFactory.get_current_tick_size()) and value1 <= (value2 + SwingFactory.get_current_tick_size()):
            return True
        return False
    
    @staticmethod
    def get_current_tick_size() -> float:
        """Get the current tick size"""
        # In Python we'll use a global or class variable instead of GlobalVariableGet
        return TICK_SIZE  # Use the constant defined in Type.py
    
    @staticmethod
    def get_all_swing_from(degree: Degree,
                          rates_total: int,
                          time: List[datetime],
                          open_prices: List[float],
                          high_prices: List[float],
                          low_prices: List[float],
                          close_prices: List[float],
                          swing_size: float) -> int:
        """Find and record all swings with size >= swing_size"""
        # Ensure rates_total is valid
        if rates_total <= 0:
            return 0
            
        # Assign swing size to degree
        degree.swing_size = swing_size
        
        # Find & record all swing with size >= swing_size
        swing_count = 0
        first_line_index = 0
        limit = max(0, rates_total - 5000)  # Ensure limit is not negative
        
        # Init for current swing
        current_swing = Swing()
        current_swing.direction = SwingDirection.SIDE_WAY
        current_swing.size = TICK_SIZE
        current_swing.high = None
        current_swing.low = None
        current_swing.timeHigh = None
        current_swing.timeLow = None
        
        # Detect First Swing
        for start in range(limit, rates_total):
            # Record candle data for current index
            _open = open_prices[start]
            _close = close_prices[start]
            _high = high_prices[start]
            _low = low_prices[start]
            
            # Detect candle direction
            if _close > _open:
                candle_direction = SwingDirection.UP
            elif _close == _open:
                candle_direction = SwingDirection.SIDE_WAY
            else:
                candle_direction = SwingDirection.DOWN
                
            # If is very first swing then just update current candle data
            if current_swing.high is None or current_swing.low is None:
                current_swing.direction = candle_direction
                current_swing.high = _high
                current_swing.low = _low
                current_swing.lowIndex = start
                current_swing.highIndex = start
                current_swing.size = abs(current_swing.high - current_swing.low)
                current_swing.timeHigh = time[start]
                current_swing.timeLow = time[start]
                
                # Find first swing then break and record the index for continue loop
                if SwingFactory.value_is_valid_with_tick_range(current_swing.size, swing_size):
                    first_line_index = start
                    break
            
            # Market make Higher High
            if _high >= current_swing.high:
                current_swing.high = high_prices[start]
                current_swing.highIndex = start
                current_swing.direction = SwingDirection.UP
                current_swing.size = abs(current_swing.high - current_swing.low)
                current_swing.timeHigh = time[start]
                
                # Find first swing then break and record the index for continue loop
                if SwingFactory.value_is_valid_with_tick_range(current_swing.size, swing_size):
                    first_line_index = start
                    break
            
            # Market make lower low
            if _low <= current_swing.low:
                current_swing.low = low_prices[start]
                current_swing.lowIndex = start
                current_swing.direction = SwingDirection.DOWN
                current_swing.timeLow = time[start]
                current_swing.size = abs(current_swing.high - current_swing.low)
                
                # Find first swing then break and record the index for continue loop
                if SwingFactory.value_is_valid_with_tick_range(current_swing.size, swing_size):
                    first_line_index = start
                    break
            
            # Market create new candles that make both Higher High & lower low
            if (_low <= current_swing.low) and (_high >= current_swing.high):
                current_swing.direction = candle_direction
                current_swing.high = _high
                current_swing.low = _low
                current_swing.lowIndex = start
                current_swing.highIndex = start
                current_swing.size = abs(current_swing.high - current_swing.low)
                current_swing.timeHigh = time[start]
                current_swing.timeLow = time[start]
                
                # Find first swing then break and record the index for continue loop
                if SwingFactory.value_is_valid_with_tick_range(current_swing.size, swing_size):
                    first_line_index = start
                    break
        
        # Continue loop for updating current swing & find future swing
        for next_bar in range(first_line_index + 1, rates_total):
            # Record candle data for current index
            _open = open_prices[next_bar]
            _close = close_prices[next_bar]
            _high = high_prices[next_bar]
            _low = low_prices[next_bar]
            
            # Detect candle direction
            if _close > _open:
                candle_direction = SwingDirection.UP
            elif _close == _open:
                candle_direction = SwingDirection.SIDE_WAY
            else:
                candle_direction = SwingDirection.DOWN
            
            # If current direction is Up and the candle make new high then update the current swing
            is_swing_continue_moving = False
            is_current_swing_side_way = False
            
            if _high > current_swing.high and _low < current_swing.low:
                is_current_swing_side_way = True
            else:
                if current_swing.direction == SwingDirection.UP and _high >= current_swing.high:
                    # Update new high
                    current_swing.pre_high = current_swing.high
                    current_swing.high = _high
                    current_swing.timeHigh = time[next_bar]
                    current_swing.highIndex = next_bar
                    # Update swing size
                    current_swing.size = abs(current_swing.low - _high)
                    is_swing_continue_moving = True
                
                # If current direction is Down and the candle make new low then update the current swing
                if current_swing.direction == SwingDirection.DOWN and _low <= current_swing.low:
                    # Update new low
                    current_swing.pre_low = current_swing.low
                    current_swing.low = _low
                    current_swing.lowIndex = next_bar
                    current_swing.timeLow = time[next_bar]
                    # Update swing size
                    current_swing.size = abs(current_swing.high - _low)
                    is_swing_continue_moving = True
            
            # Continue find next high or low if not meet current swing size
            if not SwingFactory.value_is_valid_with_tick_range(current_swing.size, swing_size):
                continue
            
            # Detect the reverse trend & mapping with swing size then push current swing to the degree
            # and begin new loop for next swing
            # Check if the reverse to new direction from pivot point
            # First one check if the reverse with only one bar
            is_have_swing_with_one_candle = False
            
            if SwingFactory.value_is_valid_with_tick_range(abs(_high - _low), swing_size) and not is_swing_continue_moving:
                # Check if need double check
                is_need_double_check = False
                if _high >= current_swing.high and _low <= current_swing.low:
                    is_need_double_check = True
                
                # Update current swing first
                if is_need_double_check:
                    if current_swing.direction == SwingDirection.UP and _high >= current_swing.high:
                        # Update new high
                        current_swing.pre_high = current_swing.high
                        current_swing.high = _high
                        current_swing.timeHigh = time[next_bar]
                        current_swing.highIndex = next_bar
                        # Update swing size
                        current_swing.size = abs(current_swing.low - _high)
                    
                    # If current direction is Down and the candle make new low then update the current swing
                    if current_swing.direction == SwingDirection.DOWN and _low <= current_swing.low:
                        # Update new low
                        current_swing.pre_low = current_swing.low
                        current_swing.low = _low
                        current_swing.lowIndex = next_bar
                        current_swing.timeLow = time[next_bar]
                        # Update swing size
                        current_swing.size = abs(current_swing.high - _low)
                
                # Update new direction if the direction is different between currentSwing & current Bar
                if ((current_swing.direction == SwingDirection.DOWN) and (_high > current_swing.high or candle_direction == SwingDirection.UP)) or \
                   ((current_swing.direction == SwingDirection.UP) and (_low < current_swing.low or candle_direction == SwingDirection.DOWN)):
                    
                    if current_swing.direction == SwingDirection.UP:
                        # Append to degree.swings
                        degree.swings.append(current_swing)
                        # Increase swing index to +1
                        swing_count += 1
                        # Change currentSwing to new direction
                        current_swing.direction = SwingDirection.DOWN
                        current_swing.low = _low
                        current_swing.lowIndex = next_bar
                        current_swing.timeLow = time[next_bar]
                        # Update current swing size
                        current_swing.size = abs(current_swing.low - current_swing.high)
                        is_have_swing_with_one_candle = True
                    
                    elif current_swing.direction == SwingDirection.DOWN:
                        # Append to degree.swings
                        degree.swings.append(current_swing)
                        # Increase swing index to +1
                        swing_count += 1
                        # Change currentSwing to new direction
                        current_swing.direction = SwingDirection.UP
                        current_swing.high = _high
                        current_swing.highIndex = next_bar
                        current_swing.timeHigh = time[next_bar]
                        # Update current swing size
                        current_swing.size = abs(current_swing.low - current_swing.high)
                        is_have_swing_with_one_candle = True
            
            if (not is_have_swing_with_one_candle and not is_swing_continue_moving) or is_current_swing_side_way:
                # Check if the reverse to new direction from pivot point
                if current_swing.direction == SwingDirection.UP:
                    if SwingFactory.value_is_valid_with_tick_range(abs(current_swing.high - _low), swing_size):
                        # Append to degree.swings
                        degree.swings.append(current_swing)
                        # Increase swing index to +1
                        swing_count += 1
                        # Change currentSwing to new direction
                        current_swing.direction = SwingDirection.DOWN
                        current_swing.low = _low
                        current_swing.lowIndex = next_bar
                        current_swing.timeLow = time[next_bar]
                        # Update current swing size
                        current_swing.size = abs(current_swing.high - _low)
                
                elif current_swing.direction == SwingDirection.DOWN:
                    if SwingFactory.value_is_valid_with_tick_range(abs(current_swing.low - _high), swing_size):
                        # Append to degree.swings
                        degree.swings.append(current_swing)
                        # Increase swing index to +1
                        swing_count += 1
                        # Change currentSwing to new direction
                        current_swing.direction = SwingDirection.UP
                        current_swing.high = _high
                        current_swing.highIndex = next_bar
                        current_swing.timeHigh = time[next_bar]
                        # Update current swing size
                        current_swing.size = abs(current_swing.low - _high)
            
            # Handle the case when we're at the last bar
            if next_bar == rates_total - 1:
                if current_swing.direction in (SwingDirection.UP, SwingDirection.DOWN):
                    # Append to degree.swings
                    degree.swings.append(current_swing)
                    # Increase swing index to +1
                    swing_count += 1
        
        degree.swing_count = swing_count
        return 1
    
    @staticmethod
    def update_swing_if_need(degree_manager, degree_update_index: int, swings: List[Swing]) -> bool:
        """Update swing if needed - adapts the MQL5 version for Python/Freqtrade
        
        Args:
            degree_manager: The DegreeManager instance
            degree_update_index: The index of the degree to update
            swings: List to store updated swings
            
        Returns:
            bool: True if an update was needed, False otherwise
        """
        is_need_update_line = False
        
        # Make sure we have degrees to update
        if degree_manager.degree_count <= 0 or degree_update_index >= degree_manager.degree_count:
            return False
            
        # Get the latest price data (in Freqtrade this would come from the strategy dataframe)
        # For now we'll assume these values are provided from somewhere else
        # These would need to be adapted to get the latest candle in Freqtrade
        for start in range(degree_manager.degree_count):
            current_degree = degree_manager.degrees[start]
            swing_size = current_degree.swing_size
            
            # Check if we have swings to update
            if current_degree.swing_count <= 0:
                continue
                
            # Get latest swing
            current_swing = current_degree.swings[current_degree.swing_count - 1]
            
            # Get latest candle data
            # In a real implementation, this would come from the latest candle in Freqtrade
            if len(current_degree.close) <= 0 or len(current_degree.open) <= 0 or \
               len(current_degree.high) <= 0 or len(current_degree.low) <= 0 or \
               len(current_degree.time) <= 0:
                continue
                
            _open = current_degree.open[-1]
            _close = current_degree.close[-1]
            _high = current_degree.high[-1]
            _low = current_degree.low[-1]
            _time = current_degree.time[-1]
            
            # Detect candle direction
            candle_direction = SwingDirection.SIDE_WAY
            if _close > _open:
                candle_direction = SwingDirection.DOWN  # In MQL5 this is DOWN
            elif _close < _open:
                candle_direction = SwingDirection.UP    # In MQL5 this is UP
            else:
                candle_direction = SwingDirection.SIDE_WAY
                
            # Process possible swing updates
            is_swing_continue_moving = False
            is_current_swing_side_way = False
            
            if _high > current_swing.high and _low < current_swing.low:
                is_current_swing_side_way = True
            else:
                # Check if current UP swing is extending higher
                if current_swing.direction == SwingDirection.UP and _high > current_swing.high:
                    # Update new high
                    current_swing.pre_high = current_swing.high
                    current_swing.high = _high
                    current_swing.pre_timeHigh = current_swing.timeHigh
                    current_swing.timeHigh = _time
                    # Update swing size
                    current_swing.size = abs(current_swing.low - _high)
                    # Update to current degree
                    current_degree.swings[current_degree.swing_count - 1] = current_swing
                    # Update direction and other properties
                    from . import DegreeManager
                    current_degree.direction = DegreeManager.DegreeManager.direction(current_degree)
                    current_degree.rates_total = len(current_degree.close)
                    # Detect patterns
                    GeometryManager.detect_brycle_xabcd(current_degree)
                    GeometryManager.detect_support_and_resistance_for(current_degree)
                    # Update in degree manager
                    degree_manager.degrees[start] = current_degree
                    is_swing_continue_moving = True
                    
                    if degree_update_index == start:
                        is_need_update_line = True
                        # Update swing in return array
                        swings[0] = current_swing
                
                # Check if current DOWN swing is extending lower
                if current_swing.direction == SwingDirection.DOWN and _low < current_swing.low:
                    # Update new low
                    current_swing.pre_low = current_swing.low
                    current_swing.low = _low
                    current_swing.pre_timeLow = current_swing.timeLow
                    current_swing.timeLow = _time
                    # Update swing size
                    current_swing.size = abs(current_swing.high - _low)
                    # Update to current degree
                    current_degree.swings[current_degree.swing_count - 1] = current_swing
                    # Update direction and other properties
                    from . import DegreeManager
                    current_degree.direction = DegreeManager.DegreeManager.direction(current_degree)
                    current_degree.rates_total = len(current_degree.close)
                    # Detect patterns
                    GeometryManager.detect_brycle_xabcd(current_degree)
                    GeometryManager.detect_support_and_resistance_for(current_degree)
                    # Update in degree manager
                    degree_manager.degrees[start] = current_degree
                    is_swing_continue_moving = True
                    
                    if degree_update_index == start:
                        is_need_update_line = True
                        # Update swing in return array
                        swings[0] = current_swing
            
            # Continue to next degree if swing size requirement not met
            if not SwingFactory.value_is_valid_with_tick_range(current_swing.size, swing_size):
                from . import DegreeManager
                current_degree.direction = DegreeManager.DegreeManager.direction(current_degree)
                current_degree.rates_total = len(current_degree.close)
                GeometryManager.detect_support_and_resistance_for(current_degree)
                continue
                
            # Check for new swing with single candle
            is_have_swing_with_one_candle = False
            
            if SwingFactory.value_is_valid_with_tick_range(abs(_high - _low), swing_size) and not is_swing_continue_moving:
                # Check if need double check
                is_need_double_check = False
                if _high >= current_swing.high and _low <= current_swing.low:
                    is_need_double_check = True
                
                # Update current swing first if needed
                if is_need_double_check:
                    # For UP swing
                    if current_swing.direction == SwingDirection.UP and _high > current_swing.high:
                        current_swing.pre_high = current_swing.high
                        current_swing.high = _high
                        current_swing.pre_timeHigh = current_swing.timeHigh
                        current_swing.timeHigh = _time
                        current_swing.size = abs(current_swing.low - _high)
                        
                        # Update degree data
                        current_degree.swings[current_degree.swing_count - 1] = current_swing
                        from . import DegreeManager
                        current_degree.direction = DegreeManager.DegreeManager.direction(current_degree)
                        current_degree.rates_total = len(current_degree.close)
                        GeometryManager.detect_brycle_xabcd(current_degree)
                        GeometryManager.detect_support_and_resistance_for(current_degree)
                        degree_manager.degrees[start] = current_degree
                        is_swing_continue_moving = True
                        
                        if degree_update_index == start:
                            is_need_update_line = True
                            swings[0] = current_swing
                    
                    # For DOWN swing
                    if current_swing.direction == SwingDirection.DOWN and _low < current_swing.low:
                        current_swing.pre_low = current_swing.low
                        current_swing.low = _low
                        current_swing.pre_timeLow = current_swing.timeLow
                        current_swing.timeLow = _time
                        current_swing.size = abs(current_swing.high - _low)
                        
                        # Update degree data
                        current_degree.swings[current_degree.swing_count - 1] = current_swing
                        from . import DegreeManager
                        current_degree.direction = DegreeManager.DegreeManager.direction(current_degree)
                        current_degree.rates_total = len(current_degree.close)
                        GeometryManager.detect_brycle_xabcd(current_degree)
                        GeometryManager.detect_support_and_resistance_for(current_degree)
                        degree_manager.degrees[start] = current_degree
                        is_swing_continue_moving = True
                        
                        if degree_update_index == start:
                            is_need_update_line = True
                            swings[0] = current_swing
                
                # Check for direction change
                if ((current_swing.direction == SwingDirection.DOWN and (_high > current_swing.pre_high)) or
                    (current_swing.direction == SwingDirection.UP and (_low < current_swing.pre_low))):
                    
                    # Handle DOWN to UP transition
                    if current_swing.direction == SwingDirection.DOWN:
                        # Create new UP swing
                        new_swing = Swing()
                        new_swing.direction = SwingDirection.UP
                        new_swing.low = _low
                        new_swing.timeLow = _time
                        new_swing.size = abs(new_swing.low - current_swing.high)
                        
                        # Add to degree
                        current_degree.swings.append(new_swing)
                        current_degree.swing_count += 1
                        
                        # Update direction and other properties
                        from . import DegreeManager
                        current_degree.direction = DegreeManager.DegreeManager.direction(current_degree)
                        current_degree.rates_total = len(current_degree.close)
                        GeometryManager.detect_brycle_xabcd(current_degree)
                        GeometryManager.detect_support_and_resistance_for(current_degree)
                        degree_manager.degrees[start] = current_degree
                        is_have_swing_with_one_candle = True
                        
                        if degree_update_index == start:
                            is_need_update_line = True
                            if len(swings) > 1:
                                swings[1] = new_swing
                        
                        continue
                    
                    # Handle UP to DOWN transition
                    if current_swing.direction == SwingDirection.UP:
                        # Create new DOWN swing
                        new_swing = Swing()
                        new_swing.direction = SwingDirection.DOWN
                        new_swing.high = _high
                        new_swing.timeHigh = _time
                        new_swing.size = abs(new_swing.high - current_swing.low)
                        
                        # Add to degree
                        current_degree.swings.append(new_swing)
                        current_degree.swing_count += 1
                        
                        # Update direction and other properties
                        from . import DegreeManager
                        current_degree.direction = DegreeManager.DegreeManager.direction(current_degree)
                        current_degree.rates_total = len(current_degree.close)
                        GeometryManager.detect_brycle_xabcd(current_degree)
                        GeometryManager.detect_support_and_resistance_for(current_degree)
                        degree_manager.degrees[start] = current_degree
                        is_have_swing_with_one_candle = True
                        
                        if degree_update_index == start:
                            is_need_update_line = True
                            if len(swings) > 1:
                                swings[1] = new_swing
                        
                        continue
            
            # Check for reversal from pivot point
            if (not is_have_swing_with_one_candle and not is_swing_continue_moving) or is_current_swing_side_way:
                # For UP swing checking for reversal down
                if current_swing.direction == SwingDirection.UP:
                    if SwingFactory.value_is_valid_with_tick_range(abs(current_swing.high - _low), swing_size):
                        # Create new DOWN swing
                        new_swing = Swing()
                        new_swing.direction = SwingDirection.DOWN
                        new_swing.high = _high
                        new_swing.low = _low
                        new_swing.timeLow = _time
                        new_swing.size = abs(current_swing.high - _low)
                        
                        # Add to degree
                        current_degree.swings.append(new_swing)
                        current_degree.swing_count += 1
                        
                        # Update direction and other properties
                        from . import DegreeManager
                        current_degree.direction = DegreeManager.DegreeManager.direction(current_degree)
                        current_degree.rates_total = len(current_degree.close)
                        GeometryManager.detect_brycle_xabcd(current_degree)
                        GeometryManager.detect_support_and_resistance_for(current_degree)
                        degree_manager.degrees[start] = current_degree
                        
                        if degree_update_index == start:
                            is_need_update_line = True
                            if len(swings) > 1:
                                swings[1] = new_swing
                    
                    continue
                
                # For DOWN swing checking for reversal up
                if current_swing.direction == SwingDirection.DOWN:
                    if SwingFactory.value_is_valid_with_tick_range(abs(current_swing.low - _high), swing_size):
                        # Create new UP swing
                        new_swing = Swing()
                        new_swing.direction = SwingDirection.UP
                        new_swing.high = _high
                        new_swing.low = _low
                        new_swing.timeHigh = _time
                        new_swing.size = abs(current_swing.low - _high)
                        
                        # Add to degree
                        current_degree.swings.append(new_swing)
                        current_degree.swing_count += 1
                        
                        # Update direction and other properties
                        from . import DegreeManager
                        current_degree.direction = DegreeManager.DegreeManager.direction(current_degree)
                        current_degree.rates_total = len(current_degree.close)
                        GeometryManager.detect_brycle_xabcd(current_degree)
                        GeometryManager.detect_support_and_resistance_for(current_degree)
                        degree_manager.degrees[start] = current_degree
                        
                        if degree_update_index == start:
                            is_need_update_line = True
                            if len(swings) > 1:
                                swings[1] = new_swing
                    
                    continue
            
            # Update geometry even if no swing changes
            current_degree.rates_total = len(current_degree.close)
            GeometryManager.detect_brycle_xabcd(current_degree)
            GeometryManager.detect_support_and_resistance_for(current_degree)
            degree_manager.degrees[start] = current_degree
        
        return is_need_update_line