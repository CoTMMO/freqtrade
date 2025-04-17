from typing import List, Dict, Optional, Tuple
import math
from .Type import Degree, SwingDirection, SupportAndResistance, GeometryType, BRYCLE_STYLE, XABCD_TYPE, RHYTHM_GEOMETRY, TradeState
from .SwingFactory import SwingFactory  # For getting price from swing and tick size

# Global constants matching MQL5 implementation
golden_ratio = [0.236, 0.25, 0.333, 0.354, 0.382, 0.447, 0.500, 0.577, 0.618, 0.667, 0.707, 0.75, 0.875, 1.000, 1.272, 1.414, 1.618, 1.732, 1.902, 2.000, 2.236, 2.618, 3.000, 4.000, 5.000]
golden_ratio_full_version = [0.111, 0.125, 0.146, 0.177, 0.186, 0.192, 0.2, 0.236, 0.250, 0.293, 0.300, 0.309, 0.333, 0.354, 0.366, 0.382, 0.408, 0.414, 0.447, 0.486, 0.500, 0.526, 0.577, 0.586, 0.618, 0.634, 0.636, 0.667, 0.691, 0.707, 0.75, 0.764, 0.786, 0.809, 0.828, 0.875, 1.000, 1.172, 1.236, 1.272, 1.309, 1.333, 1.414, 1.500, 1.618, 1.707, 1.732, 2.000, 2.058, 2.236, 2.288, 2.414, 2.618, 2.828, 3.000, 3.146, 3.464, 3.236, 3.33, 4.000, 4.236, 4.472, 5.000, 5.200, 5.388, 5.657, 6.854, 8.0, 9.000]
fibo_ser = [3.0, 5.0, 8.0, 13.0, 21.0, 34.0, 55.0, 89.0, 144.0, 233.0, 377.0, 610.0, 987.0, 1597.0, 2584.0, 4182.0, 178.0, 267.0, 356.0, 445.0, 466.0, 699.0, 932.0, 1165.0, 754.0, 1131.0, 1508.0, 1885.0]
lucas_ser = [4.0, 7.0, 11.0, 18.0, 29.0, 47.0, 76.0, 123.0, 199.0, 322.0, 521.0, 843.0, 1365.0, 2208.0, 3573.0, 5781.0]
harmonic_ser = [16.0, 23.0, 32.0, 45.0, 64.0, 91.0, 128.0, 181.0, 256.0, 362.0, 521.0, 724.0, 1024.0, 1448.0, 2048.0, 2896.0]
squares144 = [288.0, 432.0, 576.0, 720.0, 864.0, 1008.0, 1152.0, 1296.0, 1440.0, 1584.0, 1728.0, 1872.0, 2016.0, 2160.0, 2304.0, 2448.0, 2592.0, 2736.0, 2880.0, 3024.0, 3168.0, 3312.0, 3456.0]
gann_squares = [49.0, 64.0, 81.0, 100.0, 121.0, 144.0, 169.0, 196.0, 225.0, 256.0, 289.0, 324.0, 361.0, 400.0, 441.0, 484.0, 529.0, 576.0, 625.0, 676.0, 729.0, 784.0, 841.0, 900.0]
gann_cubes = [27.0, 64.0, 125.0, 216.0, 343.0, 512.0, 729.0, 1000.0, 1331.0, 1728.0, 2197.0, 2744.0, 3375.0, 4096.0, 4913.0, 5832.0, 6859.0, 8000.0, 9261.0]
solar_degree = [72.0, 90.0, 120.0, 144.0, 180.0, 223.0, 240.0, 255.0, 270.0, 288.0, 300.0, 315.0, 360.0, 432.0, 450.0, 480.0, 509.0, 540.0, 582.0, 600.0, 615.0, 624.0, 630.0, 720.0]
golden_means_ratio = [0.236, 0.382, 0.618, 0.786, 1.272, 1.618, 2.236, 2.618]
harmonic_ratio = [0.25, 0.354, 0.5, 0.707, 1.414, 2.0, 2.828, 4.0]
arithmetic_ratio = [0.333, 0.667, 0.75, 0.875, 1.333, 1.500]

class GeometryManager:
    """Implements geometry-related functionality for price analysis"""
    
    @staticmethod
    def get_rhythm_geometry(ratio: float) -> RHYTHM_GEOMETRY:
        """Determine the rhythm geometry type based on the ratio value"""
        for r in golden_means_ratio:
            if r == ratio:
                return RHYTHM_GEOMETRY.GOLDEN_MEAN
                
        for r in harmonic_ratio:
            if r == ratio:
                return RHYTHM_GEOMETRY.HARMORNIC
                
        for r in arithmetic_ratio:
            if r == ratio:
                return RHYTHM_GEOMETRY.ARITHMETIC
                
        return RHYTHM_GEOMETRY.OTHER
    
    @staticmethod
    def golden_mean_is_meet(d: float, check: float, range_value: float) -> bool:
        """Check if a value meets the golden mean criteria within a tolerance"""
        is_meet = False
        # In Python implementation, we'll need to get tick_size from a configuration or pass it as parameter
        tick_size = SwingFactory.get_current_tick_size()  # This should be implemented in SwingFactory
        
        sum_ticks_range = range_value / tick_size
        
        if sum_ticks_range <= 50:
            if d <= check + tick_size and d >= check - tick_size:
                is_meet = True
        elif sum_ticks_range > 50 and sum_ticks_range <= 200:
            if d <= check + 2 * tick_size and d >= check - 2 * tick_size:
                is_meet = True
        elif sum_ticks_range > 200 and sum_ticks_range <= 800:
            if d <= check + 3 * tick_size and d >= check - 3 * tick_size:
                is_meet = True
        elif sum_ticks_range > 800 and sum_ticks_range <= 3200:
            if d <= check + 4 * tick_size and d >= check - 4 * tick_size:
                is_meet = True
        elif sum_ticks_range > 3200:
            if d <= check + 5 * tick_size and d >= check - 5 * tick_size:
                is_meet = True
                
        return is_meet
    
    @staticmethod
    def detect_support_and_resistance_for(degree: Degree) -> None:
        """Detect support and resistance levels for a degree"""
        # Initialize the SandR array and count
        degree.SandR = []
        degree.SandR_count = 0
        
        # Need at least 5 swings to perform proper analysis
        if degree.swing_count < 5:
            return
            
        # Extract key swings for analysis
        s1 = degree.swings[degree.swing_count - 1]  # Latest swing
        s2 = degree.swings[degree.swing_count - 2]  # Previous swing
        s3 = degree.swings[degree.swing_count - 3]  # 3rd swing
        s4 = degree.swings[degree.swing_count - 4]  # 4th swing
        s5 = degree.swings[degree.swing_count - 5]  # 5th swing
        
        # Get the price point of first swing
        first_swing = s1
        first_swing_price = SwingFactory.get_price_from_swing(first_swing)
        
        # Get the price point of first swing shifted by 1
        first_swing_shift1 = s2
        first_swing_shift1_price = SwingFactory.get_price_from_swing(first_swing_shift1)
        
        # Get the price of last swing in the degree
        last_swing = degree.swings[degree.swing_count - degree.legs]
        last_swing_price = SwingFactory.get_price_from_swing(last_swing)
        
        # Initialize price check variables
        price_check = 0.0
        price_check_index = 0
        
        # Handle different market states (TRENDING, CORRECTION, OVERBALANCED, STUCK)
        if degree.state == "TRENDING":
            # Add most recent pivot point (high or low) as support/resistance
            if degree.swing_count >= 1:
                # Create S/R level from latest swing
                sr_level = SupportAndResistance()
                sr_level.type = GeometryType.PIVOT_POINT
                
                if s1.direction == SwingDirection.UP:
                    sr_level.s_rPrice = s1.high
                    sr_level.direction = SwingDirection.UP
                else:
                    sr_level.s_rPrice = s1.low
                    sr_level.direction = SwingDirection.DOWN
                    
                sr_level.size = s1.size
                sr_level.range = abs(s1.high - s1.low)
                sr_level.isValid = True
                sr_level.tradeState = TradeState.NATURAL
                
                # Add to the degree's S&R array
                degree.SandR.append(sr_level)
                degree.SandR_count += 1
            
            # Add dynamic ratio-based support/resistance levels (Fibonacci)
            if degree.direction == SwingDirection.UP:
                # Calculate Fibonacci retracement levels (38.2%, 50%, 61.8%)
                high_point = s1.high
                low_point = s2.low
                range_value = high_point - low_point
                
                # 38.2% retracement
                sr_level = SupportAndResistance()
                sr_level.type = GeometryType.DYNAMIC_RATIO
                sr_level.s_rPrice = high_point - (range_value * 0.382)
                sr_level.ratio = 0.382
                sr_level.direction = SwingDirection.DOWN
                sr_level.range = range_value
                sr_level.isValid = True
                sr_level.tradeState = TradeState.NATURAL
                
                degree.SandR.append(sr_level)
                degree.SandR_count += 1
                
                # 50% retracement
                sr_level = SupportAndResistance()
                sr_level.type = GeometryType.DYNAMIC_RATIO
                sr_level.s_rPrice = high_point - (range_value * 0.5)
                sr_level.ratio = 0.5
                sr_level.direction = SwingDirection.DOWN
                sr_level.range = range_value
                sr_level.isValid = True
                sr_level.tradeState = TradeState.NATURAL
                
                degree.SandR.append(sr_level)
                degree.SandR_count += 1
                
                # 61.8% retracement
                sr_level = SupportAndResistance()
                sr_level.type = GeometryType.DYNAMIC_RATIO
                sr_level.s_rPrice = high_point - (range_value * 0.618)
                sr_level.ratio = 0.618
                sr_level.direction = SwingDirection.DOWN
                sr_level.range = range_value
                sr_level.isValid = True
                sr_level.tradeState = TradeState.NATURAL
                
                degree.SandR.append(sr_level)
                degree.SandR_count += 1
                
            elif degree.direction == SwingDirection.DOWN:
                # Calculate Fibonacci retracement levels (38.2%, 50%, 61.8%)
                low_point = s1.low
                high_point = s2.high
                range_value = high_point - low_point
                
                # 38.2% retracement
                sr_level = SupportAndResistance()
                sr_level.type = GeometryType.DYNAMIC_RATIO
                sr_level.s_rPrice = low_point + (range_value * 0.382)
                sr_level.ratio = 0.382
                sr_level.direction = SwingDirection.UP
                sr_level.range = range_value
                sr_level.isValid = True
                sr_level.tradeState = TradeState.NATURAL
                
                degree.SandR.append(sr_level)
                degree.SandR_count += 1
                
                # 50% retracement
                sr_level = SupportAndResistance()
                sr_level.type = GeometryType.DYNAMIC_RATIO
                sr_level.s_rPrice = low_point + (range_value * 0.5)
                sr_level.ratio = 0.5
                sr_level.direction = SwingDirection.UP
                sr_level.range = range_value
                sr_level.isValid = True
                sr_level.tradeState = TradeState.NATURAL
                
                degree.SandR.append(sr_level)
                degree.SandR_count += 1
                
                # 61.8% retracement
                sr_level = SupportAndResistance()
                sr_level.type = GeometryType.DYNAMIC_RATIO
                sr_level.s_rPrice = low_point + (range_value * 0.618)
                sr_level.ratio = 0.618
                sr_level.direction = SwingDirection.UP
                sr_level.range = range_value
                sr_level.isValid = True
                sr_level.tradeState = TradeState.NATURAL
                
                degree.SandR.append(sr_level)
                degree.SandR_count += 1
                
            # Additional support/resistance detection for specific swing patterns
            # would go here (similar to MQL5 implementation)
    
    @staticmethod
    def detect_brycle_xabcd(degree: Degree) -> None:
        """Detect XABCD patterns (Brycle patterns) for a degree"""
        # Clear existing arrays
        degree.BcD = []
        degree.Alt1 = []
        degree.XcD = []
        degree.XaD = []
        degree.Rx = []
        degree.Dx = []
        degree.Alt2 = []
        degree.Ix = []
        degree.Ox = []
        
        # Need at least 5 swings to form an XABCD pattern
        if degree.swing_count < 5:
            return
        
        # Get the relevant swings for analysis (X, A, B, C, D points)
        d_swing = degree.swings[degree.swing_count - 1]
        c_swing = degree.swings[degree.swing_count - 2]
        b_swing = degree.swings[degree.swing_count - 3]
        a_swing = degree.swings[degree.swing_count - 4]
        x_swing = degree.swings[degree.swing_count - 5]
        
        sum_ratio = len(golden_ratio)
        
        if degree.state == "TRENDING":
            # BCD Pattern Analysis
            # Process B-C-D points for trending market
            b = b_swing.high if b_swing.direction == SwingDirection.UP else b_swing.low
            c = c_swing.high if c_swing.direction == SwingDirection.UP else c_swing.low
            d = d_swing.high if d_swing.direction == SwingDirection.UP else d_swing.low
            
            # Golden Means
            sum_count = 0
            for i in range(sum_ratio):
                style = BRYCLE_STYLE()
                style.type = XABCD_TYPE.BCD
                style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                style.ratio = golden_ratio[i]
                style.d_meet = False
                
                if degree.direction == SwingDirection.UP:
                    style.price = c + c_swing.size * golden_ratio[i]
                else:
                    style.price = c - c_swing.size * golden_ratio[i]
                    
                if GeometryManager.golden_mean_is_meet(
                    d=d, 
                    check=style.price, 
                    range_value=abs(d - b)
                ):
                    style.d_meet = True
                
                # Skip if price condition is not met
                if not style.d_meet:
                    if ((degree.direction == SwingDirection.UP and d > style.price) or 
                        (degree.direction == SwingDirection.DOWN and d < style.price)):
                        continue
                
                degree.BcD.append(style)
            
            # ALT1 Pattern Analysis (if we have at least 4 swings)
            if degree.swing_count >= 4:
                a = a_swing.high if a_swing.direction == SwingDirection.UP else a_swing.low
                
                # Golden Means for Alt1
                sum_count = 0
                for i in range(sum_ratio):
                    style = BRYCLE_STYLE()
                    style.type = XABCD_TYPE.ALT1
                    style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                    style.ratio = golden_ratio[i]
                    style.d_meet = False
                    
                    if degree.direction == SwingDirection.UP:
                        style.price = c + b_swing.size * golden_ratio[i]
                    else:
                        style.price = c - b_swing.size * golden_ratio[i]
                        
                    if GeometryManager.golden_mean_is_meet(
                        d=d, 
                        check=style.price, 
                        range_value=abs(d - a)
                    ):
                        style.d_meet = True
                    
                    # Skip if price condition is not met
                    if not style.d_meet:
                        if ((degree.direction == SwingDirection.UP and d > style.price) or 
                            (degree.direction == SwingDirection.DOWN and d < style.price)):
                            continue
                    
                    degree.Alt1.append(style)
                
                # RX Pattern Analysis
                sum_count = 0
                for i in range(sum_ratio):
                    style = BRYCLE_STYLE()
                    style.type = XABCD_TYPE.ALT1  # Using ALT1 type (same as MQL5 code)
                    style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                    style.ratio = golden_ratio[i]
                    style.d_meet = False
                    
                    if degree.direction == SwingDirection.UP:
                        style.price = a + c_swing.size * golden_ratio[i]
                    else:
                        style.price = a - c_swing.size * golden_ratio[i]
                        
                    if GeometryManager.golden_mean_is_meet(
                        d=d, 
                        check=style.price, 
                        range_value=abs(d - a)
                    ):
                        style.d_meet = True
                    
                    # Skip if price condition is not met
                    if not style.d_meet:
                        if ((degree.direction == SwingDirection.UP and d > style.price) or 
                            (degree.direction == SwingDirection.DOWN and d < style.price)):
                            continue
                    
                    degree.Rx.append(style)
            
            # XaD Pattern Analysis (if we have at least 5 swings)
            if degree.swing_count >= 5:
                x = x_swing.high if x_swing.direction == SwingDirection.UP else x_swing.low
                
                # Golden Means for XaD
                sum_count = 0
                for i in range(sum_ratio):
                    style = BRYCLE_STYLE()
                    style.type = XABCD_TYPE.XAD
                    style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                    style.ratio = golden_ratio[i]
                    style.d_meet = False
                    
                    if degree.direction == SwingDirection.UP:
                        style.price = a + a_swing.size * golden_ratio[i]
                    else:
                        style.price = a - a_swing.size * golden_ratio[i]
                        
                    if GeometryManager.golden_mean_is_meet(
                        d=d, 
                        check=style.price, 
                        range_value=abs(d - x)
                    ):
                        style.d_meet = True
                    
                    # Skip if price condition is not met
                    if not style.d_meet:
                        if ((degree.direction == SwingDirection.UP and d > style.price) or 
                            (degree.direction == SwingDirection.DOWN and d < style.price)):
                            continue
                    
                    degree.XaD.append(style)
                
                # ALT2 Pattern Analysis
                sum_count = 0
                for i in range(sum_ratio):
                    style = BRYCLE_STYLE()
                    style.type = XABCD_TYPE.ALT2
                    style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                    style.ratio = golden_ratio[i]
                    style.d_meet = False
                    
                    if degree.direction == SwingDirection.UP:
                        style.price = c + x_swing.size * golden_ratio[i]
                    else:
                        style.price = c - x_swing.size * golden_ratio[i]
                        
                    if GeometryManager.golden_mean_is_meet(
                        d=d, 
                        check=style.price, 
                        range_value=abs(d - x)
                    ):
                        style.d_meet = True
                    
                    # Skip if price condition is not met
                    if not style.d_meet:
                        if ((degree.direction == SwingDirection.UP and d > style.price) or 
                            (degree.direction == SwingDirection.DOWN and d < style.price)):
                            continue
                    
                    degree.Alt2.append(style)
        
        elif degree.state == "CORRECTION" or degree.state == "OVERBALANCED":
            # BCD Pattern Analysis for correction or overbalanced market
            b = b_swing.high if b_swing.direction == SwingDirection.UP else b_swing.low
            c = c_swing.high if c_swing.direction == SwingDirection.UP else c_swing.low
            d = d_swing.high if d_swing.direction == SwingDirection.UP else d_swing.low
            
            # Golden Means
            sum_count = 0
            for i in range(sum_ratio):
                style = BRYCLE_STYLE()
                style.type = XABCD_TYPE.BCD
                style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                style.ratio = golden_ratio[i]
                style.d_meet = False
                
                if degree.direction == SwingDirection.UP:
                    style.price = c - c_swing.size * golden_ratio[i]
                else:
                    style.price = c + c_swing.size * golden_ratio[i]
                    
                if GeometryManager.golden_mean_is_meet(
                    d=d, 
                    check=style.price, 
                    range_value=abs(d - c)
                ):
                    style.d_meet = True
                
                # Skip if price condition is not met
                if not style.d_meet:
                    if ((degree.direction == SwingDirection.UP and d < style.price) or 
                        (degree.direction == SwingDirection.DOWN and d > style.price)):
                        continue
                
                degree.BcD.append(style)
            
            # ALT1 Pattern Analysis (if we have at least 4 swings)
            if degree.swing_count >= 4:
                a = a_swing.high if a_swing.direction == SwingDirection.UP else a_swing.low
                
                # Golden Means for Alt1
                sum_count = 0
                for i in range(sum_ratio):
                    style = BRYCLE_STYLE()
                    style.type = XABCD_TYPE.ALT1
                    style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                    style.ratio = golden_ratio[i]
                    style.d_meet = False
                    
                    if degree.direction == SwingDirection.UP:
                        style.price = c - b_swing.size * golden_ratio[i]
                    else:
                        style.price = c + b_swing.size * golden_ratio[i]
                        
                    if GeometryManager.golden_mean_is_meet(
                        d=d, 
                        check=style.price, 
                        range_value=abs(d - a)
                    ):
                        style.d_meet = True
                    
                    # Skip if price condition is not met
                    if not style.d_meet:
                        if ((degree.direction == SwingDirection.UP and d < style.price) or 
                            (degree.direction == SwingDirection.DOWN and d > style.price)):
                            continue
                    
                    degree.Alt1.append(style)
            
            # XcD Pattern Analysis (if we have at least 5 swings)
            if degree.swing_count >= 5:
                x = x_swing.high if x_swing.direction == SwingDirection.UP else x_swing.low
                
                # Golden Means for XcD
                sum_count = 0
                for i in range(sum_ratio):
                    style = BRYCLE_STYLE()
                    style.type = XABCD_TYPE.XCD
                    style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                    style.ratio = golden_ratio[i]
                    style.d_meet = False
                    
                    if degree.direction == SwingDirection.UP:
                        style.price = c - abs(c - x) * golden_ratio[i]
                    else:
                        style.price = c + abs(c - x) * golden_ratio[i]
                        
                    if GeometryManager.golden_mean_is_meet(
                        d=d, 
                        check=style.price, 
                        range_value=abs(d - x)
                    ):
                        style.d_meet = True
                    
                    # Skip if price condition is not met
                    if not style.d_meet:
                        if ((degree.direction == SwingDirection.UP and d < style.price) or 
                            (degree.direction == SwingDirection.DOWN and d > style.price)):
                            continue
                    
                    degree.XcD.append(style)
        
        elif degree.state == "STUCK":
            # BCD Pattern Analysis for stuck market
            b = b_swing.high if b_swing.direction == SwingDirection.UP else b_swing.low
            c = c_swing.high if c_swing.direction == SwingDirection.UP else c_swing.low
            d = d_swing.high if d_swing.direction == SwingDirection.UP else d_swing.low
            
            # Golden Means
            sum_count = 0
            for i in range(sum_ratio):
                style = BRYCLE_STYLE()
                style.type = XABCD_TYPE.BCD
                style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                style.ratio = golden_ratio[i]
                style.d_meet = False
                
                if d_swing.direction == SwingDirection.UP:
                    style.price = c + c_swing.size * golden_ratio[i]
                else:
                    style.price = c - c_swing.size * golden_ratio[i]
                    
                if GeometryManager.golden_mean_is_meet(
                    d=d, 
                    check=style.price, 
                    range_value=abs(b - c)
                ):
                    style.d_meet = True
                
                # Skip if price condition is not met
                if not style.d_meet:
                    if ((d_swing.direction == SwingDirection.UP and d > style.price) or 
                        (d_swing.direction == SwingDirection.DOWN and d < style.price)):
                        continue
                
                degree.BcD.append(style)
            
            # ALT1 Pattern Analysis (if we have at least 4 swings)
            if degree.swing_count >= 4:
                a = a_swing.high if a_swing.direction == SwingDirection.UP else a_swing.low
                
                # Golden Means for Alt1
                sum_count = 0
                for i in range(sum_ratio):
                    style = BRYCLE_STYLE()
                    style.type = XABCD_TYPE.ALT1
                    style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                    style.ratio = golden_ratio[i]
                    style.d_meet = False
                    
                    if d_swing.direction == SwingDirection.UP:
                        style.price = c + b_swing.size * golden_ratio[i]
                    else:
                        style.price = c - b_swing.size * golden_ratio[i]
                        
                    if GeometryManager.golden_mean_is_meet(
                        d=d, 
                        check=style.price, 
                        range_value=abs(d - c)
                    ):
                        style.d_meet = True
                    
                    # Skip if price condition is not met
                    if not style.d_meet:
                        if ((d_swing.direction == SwingDirection.UP and d > style.price) or 
                            (d_swing.direction == SwingDirection.DOWN and d < style.price)):
                            continue
                    
                    degree.Alt1.append(style)
            
            if degree.swing_count >= 5:
                x = x_swing.high if x_swing.direction == SwingDirection.UP else x_swing.low
                
                # Check condition for XcD or XaD pattern
                if (d_swing.direction == SwingDirection.UP and c <= a) or (d_swing.direction == SwingDirection.DOWN and c >= a):
                    # XcD Pattern Analysis
                    sum_count = 0
                    for i in range(sum_ratio):
                        style = BRYCLE_STYLE()
                        style.type = XABCD_TYPE.XCD
                        style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                        style.ratio = golden_ratio[i]
                        style.d_meet = False
                        
                        if d_swing.direction == SwingDirection.UP:
                            style.price = c + abs(c - x) * golden_ratio[i]
                        else:
                            style.price = c - abs(c - x) * golden_ratio[i]
                            
                        if GeometryManager.golden_mean_is_meet(
                            d=d, 
                            check=style.price, 
                            range_value=abs(d - c)
                        ):
                            style.d_meet = True
                        
                        # Skip if price condition is not met
                        if not style.d_meet:
                            if ((d_swing.direction == SwingDirection.UP and d > style.price) or 
                                (d_swing.direction == SwingDirection.DOWN and d < style.price)):
                                continue
                        
                        degree.XcD.append(style)
                else:
                    # XaD Pattern Analysis
                    sum_count = 0
                    for i in range(sum_ratio):
                        style = BRYCLE_STYLE()
                        style.type = XABCD_TYPE.XAD
                        style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                        style.ratio = golden_ratio[i]
                        style.d_meet = False
                        
                        if d_swing.direction == SwingDirection.UP:
                            style.price = a + abs(a - x) * golden_ratio[i]
                        else:
                            style.price = a - abs(a - x) * golden_ratio[i]
                            
                        if GeometryManager.golden_mean_is_meet(
                            d=d, 
                            check=style.price, 
                            range_value=abs(d - c)
                        ):
                            style.d_meet = True
                        
                        # Skip if price condition is not met
                        if not style.d_meet:
                            if ((d_swing.direction == SwingDirection.UP and d > style.price) or 
                                (d_swing.direction == SwingDirection.DOWN and d < style.price)):
                                continue
                        
                        degree.XaD.append(style)
                
                # Check condition for Rx pattern
                extreme_condition = (
                    (d > a and d > b and d > c and d > x) or 
                    (x > a and x > b and x > c and x > d) or 
                    (d < a and d < b and d < c and d < x) or 
                    (x < a and x < b and x < c and x < d)
                )
                
                if extreme_condition:
                    # Rx Pattern Analysis
                    sum_count = 0
                    for i in range(sum_ratio):
                        style = BRYCLE_STYLE()
                        style.type = XABCD_TYPE.ALT1  # Using ALT1 as in MQL5 code
                        style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                        style.ratio = golden_ratio[i]
                        style.d_meet = False
                        
                        if d_swing.direction == SwingDirection.UP:
                            style.price = a + c_swing.size * golden_ratio[i]
                        else:
                            style.price = a - c_swing.size * golden_ratio[i]
                            
                        if GeometryManager.golden_mean_is_meet(
                            d=d, 
                            check=style.price, 
                            range_value=abs(d - x)
                        ):
                            style.d_meet = True
                        
                        # Skip if price condition is not met
                        if not style.d_meet:
                            if ((d_swing.direction == SwingDirection.UP and d > style.price) or 
                                (d_swing.direction == SwingDirection.DOWN and d < style.price)):
                                continue
                        
                        degree.Rx.append(style)
                    
                    # Dx Pattern Analysis
                    if extreme_condition:
                        sum_count = 0
                        for i in range(sum_ratio):
                            style = BRYCLE_STYLE()
                            style.type = XABCD_TYPE.ALT1  # Using ALT1 as in MQL5 code
                            style.rhythm = GeometryManager.get_rhythm_geometry(golden_ratio[i])
                            style.ratio = golden_ratio[i]
                            style.d_meet = False
                            
                            if d_swing.direction == SwingDirection.UP:
                                style.price = a + abs(x - c) * golden_ratio[i]
                            else:
                                style.price = a - abs(x - c) * golden_ratio[i]
                                
                            if GeometryManager.golden_mean_is_meet(
                                d=d, 
                                check=style.price, 
                                range_value=abs(d - x)
                            ):
                                style.d_meet = True
                            
                            # Skip if price condition is not met
                            if not style.d_meet:
                                if ((d_swing.direction == SwingDirection.UP and d > style.price) or 
                                    (d_swing.direction == SwingDirection.DOWN and d < style.price)):
                                    continue
                            
                            degree.Dx.append(style)