# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from freqtrade.persistence import Trade
from freqtrade.strategy import (IStrategy)

# --------------------------------
# Add your lib to import here
import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy as np
import os
import talib.abstract as ta
from scipy.ndimage import label, sum
from shared.custom_classes import CustomSender, CustomMethods
from typing import Optional

# This class is a sample. Feel free to customize it.
class CPD(IStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_notif = CustomSender()
        self.custom_methods = CustomMethods()
    """
    This is a sample strategy to inspire you.
    More information in https://www.freqtrade.io/en/latest/strategy-customization/

    You can:
        :return: a Dataframe with all mandatory indicators for the strategies
    - Rename the class name (Do not forget to update class_name)
    - Add any methods you want to build your strategy
    - Add any lib you need to build your strategy

    You must keep:
    - the lib in the section "Do not remove these libs"
    - the methods: populate_indicators, populate_entry_trend, populate_exit_trend
    You should keep:
    - timeframe, minimal_roi, stoploss, trailing_*
    """
    # Strategy interface version - allow new iterations of the strategy interface.
    # Check the documentation or the Sample strategy to get the latest version.
    INTERFACE_VERSION = 3

    # Can this strategy go short?
    can_short: bool = False

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi".
    minimal_roi = {
        "60": 0.01,
        "30": 0.02,
        "0": 0.04
    }

    # Optimal stoploss designed for the strategy.
    # This attribute will be overridden if the config file contains "stoploss".
    stoploss = -0.10

    # Trailing stoploss
    trailing_stop = False
    # trailing_only_offset_is_reached = False
    # trailing_stop_positive = 0.01
    # trailing_stop_positive_offset = 0.0  # Disabled / not configured

    # Optimal timeframe for the strategy.
    timeframe = os.environ.get('TIMEFRAME', '5m')

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # These values can be overridden in the config.
    use_exit_signal = False
    exit_profit_only = False
    ignore_roi_if_entry_signal = False

    conversion_line_period = 9
    base_line_periods = 26
    laggin_span = 52
    displacement = 26

    # Custom take profit percent
    custom_tp = 0.3

    # Custom stop loss percent
    custom_sl = 0.3

    # Check if the pivot candle has the lowest value compared to, for example, the 10 previous lows.
    lowest_pivot_range = 3

    # Number of Bearish/Bullish Candles After Pivot to Confirm It
    confirmation_pivot_candles = int(os.environ.get('CONFIRMATION_PIVOT_CANDLES', '1'))

    # Here are two options:
    # 'bullish' and 'greater_than_minimum' (gt_min).
    # If the option is 'bullish', the candles based on confirmation_pivot_candles should be bullish;
    # otherwise, their close should be greater than the close of the pivot candle.
    confirmation_pivot_candles_type = "bullish"

    # Check if the difference between the highest pivot and the pivot signal index,
    # going back 26 candles, is less than a specific number.
    diff_between_maximum_and_twenty_six_point = 5

    # If True, The Close of Last Candle In Pivot Pattern Should Be Greater Than Conversion
    close_above_conversion = True

    # If True, CPD needs divergence confirmation too
    divergence_confirmation = True

    # possible values are close and high
    entry_price_type = 'close'

    # Check if the distance, in percent, between the base and the entry price is greater than a specific value.
    entry_base_distance = 0.5

    # Determine the Starting Point for Measuring the Distance
    # to Take Profit (TP) and Base (Either at the Minimum or the Entry Candle).
    # Possible values are minimum and entry_candle
    tp_base_check_point_type = 'minimum'

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 70

    # Plot Length
    plot_candle_count = 35

    # Optional order type mapping.
    order_types = {
        'entry': 'limit',
        'exit': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    # Optional order time in force.
    order_time_in_force = {
        'entry': 'GTC',
        'exit': 'GTC'
    }

    plot_config = {
        'main_plot': {
            'tenkan_sen': {'color': 'orange'},
            'kijun_sen': {'color': 'blue'},
            'senkou_span_b': {'color': 'red'},
            'leading_senkou_span_b': {'color': 'green'},
        }
    }

    telegram_plot_config_long = {
        'main_plot': {
            'tenkan_sen': {'color': 'orange'},
            'kijun_sen': {'color': 'blue'},
            'leading_senkou_span_b': {'color': 'red'},
            'pivot_lows': {'color': 'pink'},
        }
    }

    telegram_plot_config_short = {
        'main_plot': {
            'tenkan_sen': {'color': 'orange'},
            'kijun_sen': {'color': 'blue'},
            'leading_senkou_span_b': {'color': 'red'},
            'maximum_lines': {'color': 'aqua'},
        },
        'sub_plot': {
            'rsi': {'color': 'blue'}
        }
    }


    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        These pair/interval combinations are non-tradeable, unless they are part
        of the whitelist as well.
        For more information, please consult the documentation
        :return: List of tuples in the format (pair, interval)
            Sample: return [("ETH/USDT", "5m"),
                            ("BTC/USDT", "15m"),
                            ]
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        :param dataframe: Dataframe with data from the exchange
        :param metadata: Additional information, like the currently traded pair
        :return: a Dataframe with all mandatory indicators for the strategies
        """

        # Ichi
        ichi_ = self.custom_methods.ichimoku(dataframe=dataframe,
                              conversion_line_period=self.conversion_line_period,
                              base_line_periods=self.base_line_periods,
                              laggin_span=self.laggin_span,
                              displacement=self.displacement
                              )

        dataframe['tenkan_sen'] = ichi_['tenkan_sen']
        dataframe['kijun_sen'] = ichi_['kijun_sen']
        dataframe['senkou_span_a'] = ichi_['senkou_span_a']
        dataframe['senkou_span_b'] = ichi_['senkou_span_b']
        dataframe['leading_senkou_span_a'] = ichi_['leading_senkou_span_a']
        dataframe['leading_senkou_span_b'] = ichi_['leading_senkou_span_b']
        dataframe['chikou_span'] = ichi_['chikou_span']
        dataframe['cloud_green'] = ichi_['cloud_green']
        dataframe['cloud_red'] = ichi_['cloud_red']

        ############## Long Signals ##############
        dataframe=self.custom_methods.find_pivot_lows(df=dataframe,
                                                      lowest_pivot_range=self.lowest_pivot_range,
                                                      confirmation_pivot_candles=self.confirmation_pivot_candles,
                                                      confirmation_pivot_candles_type=self.confirmation_pivot_candles_type,
                                                      diff_between_maximum_and_twenty_six_point=self.diff_between_maximum_and_twenty_six_point,
                                                      close_above_conversion=self.close_above_conversion,
                                                      divergence_confirmation=self.divergence_confirmation,
                                                      entry_price_type=self.entry_price_type,
                                                      entry_base_distance=self.entry_base_distance,
                                                      tp_base_check_point_type=self.tp_base_check_point_type)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        dataframe.loc[dataframe['long_signal'] != np.nan,
            'enter_long'] = 1
        if dataframe['long_signal'].iloc[-1] > 0:
            metadata['strategy_name'] = f"{self.__class__.__name__} (Long)"
            metadata['timeframe'] = self.timeframe
            data = dataframe.tail(self.plot_candle_count)

            candle_markers = np.full(len(data), np.nan)
            candle_markers[-9] = round(data.iloc[-9]['high'], 7)
            candle_markers[-26] = round(data.iloc[-26]['high'], 7)

            markers = {
                "data": candle_markers.tolist(),
                "color": 'darkgreen'}

            self.custom_notif.send_custom_message(self.dp, data, metadata,
                                                  plot_config=self.telegram_plot_config_long,
                                                  markers={"markers": markers})

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """

        return dataframe
