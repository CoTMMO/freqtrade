from freqtrade.strategy.interface import IStrategy
from freqtrade.strategy import merge_informative_pair
import pandas as pd
from freqtrade.PA_Engine.DegreeManager import DegreeManager
from freqtrade.PA_Engine.Type import DegreeState, SwingDirection

class DegreeManagerSupportResStrategy(IStrategy):
    timeframe = '5m'
    minimal_roi = {"0": 0.01}
    stoploss = -0.1
    trailing_stop = False
    use_custom_stoploss = False
    process_only_new_candles = True
    startup_candle_count: int = 50

    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # Chuẩn bị dữ liệu cho DegreeManager
        dm = DegreeManager(symbol_name=metadata['pair'])
        degree_count = dm.find_all_degree_from(
            rates_total=len(dataframe),
            time=list(dataframe['date']) if 'date' in dataframe else list(dataframe.index),
            open_prices=list(dataframe['open']),
            high_prices=list(dataframe['high']),
            low_prices=list(dataframe['low']),
            close_prices=list(dataframe['close']),
            minimum_swing_size=0.5  # Có thể tối ưu tham số này
        )

        # Gắn thông tin degree vào dataframe
        dataframe['degree_trending_support'] = None
        dataframe['degree_trending_resist'] = None
        dataframe['degree_trending_sandr_price'] = None
        dataframe['degree_trending_sandr_type'] = None

        if degree_count > 0:
            for d in dm.degrees:
                if d.state == DegreeState.TRENDING:
                    for sandr in d.SandR:
                        # Lưu giá trị hỗ trợ/kháng cự vào các dòng gần giá trị đó
                        idx = (abs(dataframe['close'] - sandr.s_rPrice)).idxmin()
                        dataframe.at[idx, 'degree_trending_support' if sandr.direction == SwingDirection.UP else 'degree_trending_resist'] = sandr.s_rPrice
                        dataframe.at[idx, 'degree_trending_sandr_price'] = sandr.s_rPrice
                        dataframe.at[idx, 'degree_trending_sandr_type'] = sandr.direction.value

        return dataframe

    def populate_buy_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # Mua khi giá tiếp cận vùng hỗ trợ của degree trending
        dataframe.loc[
            (dataframe['degree_trending_support'].notnull()) &
            (abs(dataframe['close'] - dataframe['degree_trending_support'])/dataframe['close'] < 0.003),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        # Bán khi giá tiếp cận vùng kháng cự của degree trending
        dataframe.loc[
            (dataframe['degree_trending_resist'].notnull()) &
            (abs(dataframe['close'] - dataframe['degree_trending_resist'])/dataframe['close'] < 0.003),
            'sell'] = 1
        return dataframe
