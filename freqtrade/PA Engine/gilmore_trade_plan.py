from typing import List, Dict, Any, Optional
from datetime import datetime
from .Type import Degree, DegreeState, SwingDirection, TICK_SIZE
import numpy as np
import talib.abstract as ta

# Minimum confidence threshold
MIN_CONFIDENCE = 0.3

def generate_gilmore_trade_plan(
    degrees: List[Degree],
    current_price: float,
    indicators: Dict[str, Any],
    intermarket_signals: Dict[str, Any],
    key_levels: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generate potential trade plans based on Bryce Gilmore's Price Action methodology.
    Iterate through each degree, determine its state and call corresponding check functions.
    Returns a sorted list of plan dicts by confidence.
    """
    plans: List[Dict[str, Any]] = []
    for degree in degrees:
        state = degree.state
        if state == DegreeState.TRENDING:
            plans.extend(_check_trending_plans(degree, current_price, indicators,
                                              intermarket_signals, key_levels))
        elif state == DegreeState.CORRECTION:
            plans.extend(_check_correction_plans(degree, current_price, indicators,
                                                intermarket_signals, key_levels))
        elif state == DegreeState.OVERBALANCED:
            plans.extend(_check_reversal_plans(degree, current_price, indicators,
                                               intermarket_signals, key_levels))
        elif state == DegreeState.STUCK:
            plans.extend(_check_sideways_plans(degree, current_price, indicators,
                                              intermarket_signals, key_levels))
        plans.extend(_check_dd_reversal_setup(degree, current_price, indicators,
                                             intermarket_signals, key_levels))
        plans.extend(_check_break_back_setup(degree, current_price, indicators,
                                            intermarket_signals, key_levels))
    # Filter by entry and confidence
    valid_plans = [p for p in plans if p.get('entry_zone') is not None and p.get('confidence', 0.0) >= MIN_CONFIDENCE]
    # Pick best plan per degree level
    best_by_level: Dict[float, Dict[str, Any]] = {}
    for p in valid_plans:
        lvl = p.get('relevant_degree_level')
        if lvl not in best_by_level or p.get('confidence', 0.0) > best_by_level[lvl].get('confidence', 0.0):
            best_by_level[lvl] = p
    # Sort final plans by confidence
    final_plans = sorted(best_by_level.values(), key=lambda x: x.get('confidence', 0.0), reverse=True)
    return final_plans


def _check_trending_plans(
    degree: Degree,
    current_price: float,
    indicators: Dict[str, Any],
    intermarket_signals: Dict[str, Any],
    key_levels: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Refined pullback and breakout setups in an existing trend.
    """
    plans: List[Dict[str, Any]] = []
    if not degree.swings:
        return plans
    last = degree.swings[-1]
    # ATR, ADX, volume
    data = {'high': np.array(degree.high), 'low': np.array(degree.low), 'close': np.array(degree.close)}
    atr = float(ta.ATR(data, timeperiod=14)[-1]) if len(degree.high) else TICK_SIZE
    adx = float(ta.ADX(data, timeperiod=14)[-1]) if len(degree.high) else 0.0
    adx_sc = min(adx / 40.0, 1.0)
    vol = indicators.get('volume', {})
    vol_sc = 1.0 if vol.get('current', 0.0) >= vol.get('ma', 0.0) else 0.0
    threshold = atr * 0.382
    # Fibonacci retracements
    fibs = calculate_fibonacci_retracements(last.high, last.low)
    # Pullback setups
    if degree.direction == SwingDirection.UP:
        for lvl in [0.382, 0.5, 0.618]:
            price = fibs.get(lvl)
            if price and abs(current_price - price) <= threshold:
                sl = price - atr
                tp1 = last.high
                tp2 = price + (last.high - price) * 2
                conf = round(0.2 + adx_sc * 0.3 + vol_sc * 0.2, 2)
                plans.append({
                    'strategy': f"Trend Pullback {int(lvl*100)}% ({degree.swing_size} Ticks)",
                    'entry_type': 'BUY',
                    'direction': 'UP',
                    'entry_zone': price,
                    'stop_loss': sl,
                    'target_zone_1': tp1,
                    'target_zone_2': tp2,
                    'confidence': conf,
                    'notes': f"Fib{lvl}",
                    'relevant_degree_level': degree.swing_size
                })
    else:
        for lvl in [0.382, 0.5, 0.618]:
            price = fibs.get(lvl)
            if price and abs(current_price - price) <= threshold:
                sl = price + atr
                tp1 = last.low
                tp2 = price - (price - last.low) * 2
                conf = round(0.2 + adx_sc * 0.3 + vol_sc * 0.2, 2)
                plans.append({
                    'strategy': f"Trend Pullback {int(lvl*100)}% ({degree.swing_size} Ticks)",
                    'entry_type': 'SELL',
                    'direction': 'DOWN',
                    'entry_zone': price,
                    'stop_loss': sl,
                    'target_zone_1': tp1,
                    'target_zone_2': tp2,
                    'confidence': conf,
                    'notes': f"Fib{lvl}",
                    'relevant_degree_level': degree.swing_size
                })
    # Breakout setups
    if degree.direction == SwingDirection.UP and current_price > last.high + threshold and adx >= 25 and vol_sc:
        entry = last.high + TICK_SIZE
        sl = last.high
        diff = last.high - last.low
        tp1 = entry + diff
        tp2 = entry + diff * 2
        conf = round(0.3 + adx_sc * 0.2 + vol_sc * 0.3, 2)
        plans.append({
            'strategy': f"Trend Breakout ({degree.swing_size} Ticks)",
            'entry_type': 'BUY_Stop',
            'direction': 'UP',
            'entry_zone': entry,
            'stop_loss': sl,
            'target_zone_1': tp1,
            'target_zone_2': tp2,
            'confidence': conf,
            'notes': 'Breakout with ADX/Vol',
            'relevant_degree_level': degree.swing_size
        })
    if degree.direction == SwingDirection.DOWN and current_price < last.low - threshold and adx >= 25 and vol_sc:
        entry = last.low - TICK_SIZE
        sl = last.low
        diff = last.high - last.low
        tp1 = entry - diff
        tp2 = entry - diff * 2
        conf = round(0.3 + adx_sc * 0.2 + vol_sc * 0.3, 2)
        plans.append({
            'strategy': f"Trend Breakout ({degree.swing_size} Ticks)",
            'entry_type': 'SELL_Stop',
            'direction': 'DOWN',
            'entry_zone': entry,
            'stop_loss': sl,
            'target_zone_1': tp1,
            'target_zone_2': tp2,
            'confidence': conf,
            'notes': 'Breakout with ADX/Vol',
            'relevant_degree_level': degree.swing_size
        })
    return plans


def _check_correction_plans(
    degree: Degree,
    current_price: float,
    indicators: Dict[str, Any],
    intermarket_signals: Dict[str, Any],
    key_levels: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Identify setups during a correction (entries back into trend or reversals).
    """
    plans: List[Dict[str, Any]] = []
    # basic correction bounce setup using pivot swing and ATR
    if degree.swings:
        last = degree.swings[-1]
        # compute ATR via TA-Lib
        data = {'high': np.array(degree.high), 'low': np.array(degree.low), 'close': np.array(degree.close)}
        atr_series = ta.ATR(data, timeperiod=14)
        atr = float(atr_series[-1]) if len(atr_series) else 0.0
        if degree.direction == SwingDirection.UP:
            entry_zone = last.low
            sl = entry_zone - atr if atr > 0 else None
            tp1 = last.high
            confidence = 0.5
            plans.append({
                'strategy': f"Correction Bounce ({degree.swing_size} Ticks)",
                'entry_type': 'BUY',
                'direction': degree.direction.name,
                'entry_zone': entry_zone,
                'stop_loss': sl,
                'target_zone_1': tp1,
                'target_zone_2': None,
                'confidence': confidence,
                'notes': 'Correction entry back into trend',
                'relevant_degree_level': degree.swing_size
            })
        elif degree.direction == SwingDirection.DOWN:
            entry_zone = last.high
            sl = entry_zone + atr if atr > 0 else None
            tp1 = last.low
            confidence = 0.5
            plans.append({
                'strategy': f"Correction Bounce ({degree.swing_size} Ticks)",
                'entry_type': 'SELL',
                'direction': degree.direction.name,
                'entry_zone': entry_zone,
                'stop_loss': sl,
                'target_zone_1': tp1,
                'target_zone_2': None,
                'confidence': confidence,
                'notes': 'Correction entry back into trend',
                'relevant_degree_level': degree.swing_size
            })
    return plans


def _check_reversal_plans(
    degree: Degree,
    current_price: float,
    indicators: Dict[str, Any],
    intermarket_signals: Dict[str, Any],
    key_levels: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Identify reversal setups after an overbalanced correction.
    """
    plans: List[Dict[str, Any]] = []
    # basic 1:1 double-drive reversal setup using last swing and ATR
    if degree.swings:
        last = degree.swings[-1]
        # compute ATR via TA-Lib
        data = {'high': np.array(degree.high), 'low': np.array(degree.low), 'close': np.array(degree.close)}
        atr_series = ta.ATR(data, timeperiod=14)
        atr = float(atr_series[-1]) if len(atr_series) else 0.0
        drive = last.size
        if degree.direction == SwingDirection.UP:
            entry_zone = last.low
            sl = entry_zone - atr if atr > 0 else None
            tp1 = entry_zone + drive
            tp2 = entry_zone + drive * 2
            confidence = 0.6
            plans.append({
                'strategy': f"1:1 DD Reversal ({degree.swing_size} Ticks)",
                'entry_type': 'BUY',
                'direction': degree.direction.name,
                'entry_zone': entry_zone,
                'stop_loss': sl,
                'target_zone_1': tp1,
                'target_zone_2': tp2,
                'confidence': confidence,
                'notes': 'Double-drive reversal after overbalance',
                'relevant_degree_level': degree.swing_size
            })
        elif degree.direction == SwingDirection.DOWN:
            entry_zone = last.high
            sl = entry_zone + atr if atr > 0 else None
            tp1 = entry_zone - drive
            tp2 = entry_zone - drive * 2
            confidence = 0.6
            plans.append({
                'strategy': f"1:1 DD Reversal ({degree.swing_size} Ticks)",
                'entry_type': 'SELL',
                'direction': degree.direction.name,
                'entry_zone': entry_zone,
                'stop_loss': sl,
                'target_zone_1': tp1,
                'target_zone_2': tp2,
                'confidence': confidence,
                'notes': 'Double-drive reversal after overbalance',
                'relevant_degree_level': degree.swing_size
            })
    return plans


def _check_sideways_plans(
    degree: Degree,
    current_price: float,
    indicators: Dict[str, Any],
    intermarket_signals: Dict[str, Any],
    key_levels: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Refined range-bound fade and breakout setups.
    """
    plans: List[Dict[str, Any]] = []
    if not degree.swings:
        return plans
    highs = [s.high for s in degree.swings]
    lows = [s.low for s in degree.swings]
    top, bot = max(highs), min(lows)
    data = {'high': np.array(degree.high), 'low': np.array(degree.low), 'close': np.array(degree.close)}
    atr_series = ta.ATR(data, timeperiod=14)
    raw = atr_series[-1] if len(atr_series) else np.nan
    atr = float(raw) if (not np.isnan(raw) and raw > 0) else TICK_SIZE
    adx = float(ta.ADX(data, timeperiod=14)[-1]) if len(degree.high) else 0.0
    vol = indicators.get('volume', {})
    vol_cur, vol_ma = vol.get('current', 0.0), vol.get('ma', 0.0)
    # Stochastic
    slowk, slowd = ta.STOCH(data, fastk_period=14, slowk_period=3, slowd_period=3)
    k_val, d_val = float(slowk[-1]), float(slowd[-1])
    # Fade setups
    if abs(current_price - top) <= atr and k_val > 80:
        entry = top
        sl = entry + atr
        tp1 = bot
        conf = round(0.3 + (k_val > 80) * 0.2, 2)
        plans.append({
            'strategy': f"Range Fade ({degree.swing_size} Ticks)",
            'entry_type': 'SELL',
            'direction': 'DOWN',
            'entry_zone': entry,
            'stop_loss': sl,
            'target_zone_1': tp1,
            'target_zone_2': None,
            'confidence': conf,
            'notes': 'Fade at resistance',
            'relevant_degree_level': degree.swing_size
        })
    if abs(current_price - bot) <= atr and k_val < 20:
        entry = bot
        sl = entry - atr
        tp1 = top
        conf = round(0.3 + (k_val < 20) * 0.2, 2)
        plans.append({
            'strategy': f"Range Fade ({degree.swing_size} Ticks)",
            'entry_type': 'BUY',
            'direction': 'UP',
            'entry_zone': entry,
            'stop_loss': sl,
            'target_zone_1': tp1,
            'target_zone_2': None,
            'confidence': conf,
            'notes': 'Fade at support',
            'relevant_degree_level': degree.swing_size
        })
    # Breakouts requiring ADX & volume confirmation
    if current_price > top + atr and adx >= 25 and vol_cur > vol_ma * 1.2:
        entry = top + TICK_SIZE
        sl = top
        tp1 = entry + (top - bot)
        conf = round(0.4 + (adx / 50) + 0.2, 2)
        plans.append({
            'strategy': f"Range Breakout ({degree.swing_size} Ticks)",
            'entry_type': 'BUY_Stop',
            'direction': 'UP',
            'entry_zone': entry,
            'stop_loss': sl,
            'target_zone_1': tp1,
            'target_zone_2': None,
            'confidence': conf,
            'notes': 'Breakout ADX/Vol',
            'relevant_degree_level': degree.swing_size
        })
    if current_price < bot - atr and adx >= 25 and vol_cur > vol_ma * 1.2:
        entry = bot - TICK_SIZE
        sl = bot
        tp1 = entry - (top - bot)
        conf = round(0.4 + (adx / 50) + 0.2, 2)
        plans.append({
            'strategy': f"Range Breakout ({degree.swing_size} Ticks)",
            'entry_type': 'SELL_Stop',
            'direction': 'DOWN',
            'entry_zone': entry,
            'stop_loss': sl,
            'target_zone_1': tp1,
            'target_zone_2': None,
            'confidence': conf,
            'notes': 'Breakout ADX/Vol',
            'relevant_degree_level': degree.swing_size
        })
    return plans


def _check_dd_reversal_setup(degree: Degree,
                            current_price: float,
                            indicators: Dict[str, Any],
                            intermarket_signals: Dict[str, Any],
                            key_levels: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Detect AB=CD reversal at confluence zone and return plan"""
    from .SwingFactory import SwingFactory
    # require two swings for AB=CD
    if len(degree.swings) < 2:
        return None
    prev, last = degree.swings[-2], degree.swings[-1]
    if not SwingFactory.value_is_in_tick_range(prev.size, last.size):
        return None
    # entry zone via confluence
    ez = _find_entry_zone_with_confluence(degree, current_price, key_levels)
    if not ez:
        return None
    entry_price = (ez['low'] + ez['high']) / 2
    # ATR for SL/TP
    data = {'high': np.array(degree.high), 'low': np.array(degree.low), 'close': np.array(degree.close)}
    atr_series = ta.ATR(data, timeperiod=14)
    raw = atr_series[-1] if len(atr_series) else np.nan
    atr = float(raw) if (not np.isnan(raw) and raw > 0) else TICK_SIZE
    sl = _calculate_dynamic_stoploss(degree, atr)
    tp1, tp2 = _calculate_dynamic_targets(degree, atr)
    # confidence: combine confluence, divergence, volume
    div = _check_stochastic_divergence(indicators)
    div_sc = 1.0 if ((div.get('bullish') and degree.direction == SwingDirection.UP)
                    or (div.get('bearish') and degree.direction == SwingDirection.DOWN)) else 0.0
    vol = indicators.get('volume', {})
    vol_sc = 1.0 if vol.get('current', 0.0) >= vol.get('ma', 0.0) else 0.0
    base = 0.5
    conf = round(base + ez['score'] * 0.3 + div_sc * 0.1 + vol_sc * 0.1, 2)
    return {
        'strategy': f"AB=CD Reversal ({degree.swing_size} Ticks)",
        'entry_type': 'BUY' if degree.direction == SwingDirection.UP else 'SELL',
        'direction': degree.direction.name,
        'entry_zone': entry_price,
        'stop_loss': sl,
        'target_zone_1': tp1,
        'target_zone_2': tp2,
        'confidence': conf,
        'notes': f"AB=CD, {ez['notes']}",
        'relevant_degree_level': degree.swing_size
    }


def _check_break_back_setup(degree: Degree,
                           current_price: float,
                           indicators: Dict[str, Any],
                           intermarket_signals: Dict[str, Any],
                           key_levels: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Detect false-breakout back inside and return contrarian plan"""
    from .SwingFactory import SwingFactory
    if len(degree.swings) < 3:
        return None
    s1, s2, s3 = degree.swings[-3], degree.swings[-2], degree.swings[-1]
    is_false = False
    if s2.direction == SwingDirection.UP and s2.high > s1.high and s3.low <= s1.high:
        is_false = True
        entry_side = SwingDirection.DOWN
    elif s2.direction == SwingDirection.DOWN and s2.low < s1.low and s3.high >= s1.low:
        is_false = True
        entry_side = SwingDirection.UP
    if not is_false:
        return None
    ez = _find_entry_zone_with_confluence(degree, current_price, key_levels)
    if not ez:
        return None
    entry_price = (ez['low'] + ez['high']) / 2
    data = {'high': np.array(degree.high), 'low': np.array(degree.low), 'close': np.array(degree.close)}
    atr_series = ta.ATR(data, timeperiod=14)
    raw = atr_series[-1] if len(atr_series) else np.nan
    atr = float(raw) if (not np.isnan(raw) and raw > 0) else TICK_SIZE
    sl = _calculate_dynamic_stoploss(degree, atr)
    tp1, tp2 = _calculate_dynamic_targets(degree, atr)
    div = _check_stochastic_divergence(indicators)
    div_sc = 1.0 if ((div.get('bearish') and entry_side == SwingDirection.DOWN)
                    or (div.get('bullish') and entry_side == SwingDirection.UP)) else 0.0
    vol = indicators.get('volume', {})
    vol_sc = max(0.0, 1.0 - (vol.get('current', 0.0) / max(vol.get('ma', 1.0), 1.0)))
    base = 0.4
    conf = round(base + ez['score'] * 0.2 + div_sc * 0.1 + vol_sc * 0.1, 2)
    return {
        'strategy': f"False-Break ({degree.swing_size} Ticks)",
        'entry_type': 'SELL' if entry_side == SwingDirection.DOWN else 'BUY',
        'direction': entry_side.name,
        'entry_zone': entry_price,
        'stop_loss': sl,
        'target_zone_1': tp1,
        'target_zone_2': tp2,
        'confidence': conf,
        'notes': f"False-break, {ez['notes']}",
        'relevant_degree_level': degree.swing_size
    }


def _find_entry_zone_with_confluence(degree: Degree, current_price: float, key_levels: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Identify entry confluence zone: aggregates multiple S/R, fib, pivots, XABCD levels near current_price.
    Returns dict with low, high, score, levels, notes.
    """
    if not degree.swings:
        return None
    # ATR threshold
    data = {'high': np.array(degree.high), 'low': np.array(degree.low), 'close': np.array(degree.close)}
    atr_series = ta.ATR(data, timeperiod=14)
    raw = atr_series[-1] if len(atr_series) else np.nan
    atr = float(raw) if (not np.isnan(raw) and raw > 0) else TICK_SIZE
    threshold = atr
    # Collect levels
    levels: Dict[str, float] = {}
    # Support/Resistance from Degree
    for s in degree.SandR:
        if getattr(s, 'isValid', False):
            levels[f"SAR_{s.type.name}"] = s.s_rPrice
    # Fibonacci retracements and extensions from previous swing
    if len(degree.swings) >= 2:
        prev = degree.swings[-2]
        levels.update(calculate_fibonacci_retracements(prev.high, prev.low))
        levels.update(calculate_fibonacci_extensions(prev.high, prev.low))
    # Pivot points
    pivots = key_levels.get('pivots', {})
    for name, price in pivots.items():
        levels[f"PIVOT_{name}"] = price
    # BPL levels
    bpl = key_levels.get('bpl', {})
    for name, price in bpl.items():
        levels[f"BPL_{name}"] = price
    # Other key levels
    for name in ['day_open', 'globex_high', 'globex_low', 'gap_fill_target', 'prior_mob_support', 'prior_mob_resistance']:
        price = key_levels.get(name)
        if price is not None:
            levels[name.upper()] = price
    # XABCD style levels
    for attr in ['BcD', 'Alt1', 'XcD', 'XaD', 'Rx', 'Dx', 'Alt2', 'Ix', 'Ox']:
        for item in getattr(degree, attr, []):
            if getattr(item, 'isValid', False):
                levels[f"{attr}_{item.type.name}"] = item.price
    # Last swing pivots
    last = degree.swings[-1]
    levels['LAST_HIGH'] = last.high
    levels['LAST_LOW'] = last.low
    # Filter near current_price
    candidate = {k: v for k, v in levels.items() if abs(v - current_price) <= threshold}
    if not candidate:
        return None
    vals = list(candidate.values())
    low, high = min(vals), max(vals)
    # Compute confluence score
    weight_map = {
        'SAR':1.0, 'FIBO':1.5, 'EXT':1.5, 'PIVOT':1.0, 'BPL':1.2,
        'DAY_OPEN':0.8, 'GLOBEX_HIGH':0.8, 'GLOBEX_LOW':0.8, 'GAP_FILL_TARGET':1.0,
        'PRIOR_MOB_SUPPORT':1.3, 'PRIOR_MOB_RESISTANCE':1.3,
        'BcD':1.5, 'Alt1':1.2, 'XcD':1.2, 'XaD':1.2, 'Rx':1.2, 'Dx':1.2,
        'Alt2':1.2, 'Ix':1.2, 'Ox':1.2, 'LAST':1.0
    }
    total = sum(weight_map.get(k.split('_')[0], 1.0) for k in candidate.keys())
    max_w = max(weight_map.values()) * len(candidate) if candidate else 1.0
    score = round(min(total / max_w, 1.0), 2)
    notes = ','.join(candidate.keys())
    return {'low': low, 'high': high, 'score': score, 'levels': candidate, 'notes': notes}


def _calculate_confidence_score(degree: Degree,
                                indicators: Dict[str, Any],
                                intermarket_signals: Dict[str, Any],
                                key_levels: Dict[str, Any]) -> float:
    """Combine ADX, stochastic divergence, and volume for confidence (0.0-1.0)"""
    # compute ADX via TA-Lib
    data = {'high': np.array(degree.high), 'low': np.array(degree.low), 'close': np.array(degree.close)}
    adx_series = ta.ADX(data, timeperiod=14)
    adx = float(adx_series[-1]) if len(adx_series) else 0.0
    adx_score = min(adx / 40.0, 1.0)
    stoch_div = _check_stochastic_divergence(indicators)
    div_score = 1.0 if ((stoch_div.get('bullish') and degree.direction == SwingDirection.UP) or
                        (stoch_div.get('bearish') and degree.direction == SwingDirection.DOWN)) else 0.0
    vol = indicators.get('volume', {})
    vol_score = 1.0 if vol.get('current', 0.0) >= vol.get('ma', 0.0) else 0.5
    score = 0.5 * adx_score + 0.3 * div_score + 0.2 * vol_score
    return round(score, 2)


def _calculate_dynamic_stoploss(degree: Degree, atr: float) -> Optional[float]:
    """ATR-based stop-loss: a few ticks beyond last swing pivot"""
    if atr > 0 and degree.swings:
        last = degree.swings[-1]
        if degree.direction == SwingDirection.UP:
            return last.low - atr
        elif degree.direction == SwingDirection.DOWN:
            return last.high + atr
    return None


def _calculate_dynamic_targets(degree: Degree, atr: float) -> (Optional[float], Optional[float]):
    """ATR-based targets: 1x and 2x last swing size"""
    if atr > 0 and degree.swings:
        last = degree.swings[-1]
        drive = last.size
        if degree.direction == SwingDirection.UP:
            return last.low + drive, last.low + drive * 2
        elif degree.direction == SwingDirection.DOWN:
            return last.high - drive, last.high - drive * 2
    return None, None


def _check_stochastic_divergence(indicators: Dict[str, Any]) -> Dict[str, bool]:
    """Return cleaned stochastic divergence signals"""
    div = indicators.get('stoch_divergence', {})
    return {
        'bullish': bool(div.get('bullish', False)),
        'bearish': bool(div.get('bearish', False))
    }


def calculate_fibonacci_retracements(high: float, low: float) -> Dict[float, float]:
    """Return key Fibonacci retracement levels between high and low"""
    diff = high - low
    levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    return {l: high - diff * l for l in levels}


def calculate_fibonacci_extensions(high: float, low: float) -> Dict[float, float]:
    """Return key Fibonacci extension levels beyond high"""
    diff = high - low
    levels = [1.0, 1.272, 1.618, 2.0]
    return {l: high + diff * (l - 1) for l in levels}


def calculate_pivot_points(high: float, low: float, close: float) -> Dict[str, float]:
    """Compute standard pivots (P, R1/S1, R2/S2, R3/S3)"""
    P = (high + low + close) / 3.0
    R1 = 2 * P - low
    S1 = 2 * P - high
    R2 = P + (high - low)
    S2 = P - (high - low)
    R3 = high + 2 * (P - low)
    S3 = low - 2 * (high - P)
    return {'P': P, 'R1': R1, 'S1': S1, 'R2': R2, 'S2': S2, 'R3': R3, 'S3': S3}
