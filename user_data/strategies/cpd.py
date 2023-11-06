# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame

from freqtrade.strategy import (IStrategy)

# --------------------------------
# Add your lib to import here
import freqtrade.vendor.qtpylib.indicators as qtpylib
import numpy as np
import os
from scipy.ndimage import label, sum
from shared.custom_classes import CustomSender, CustomMethods


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
    can_short: bool = True

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

    confirmation_pivot_candles = int(os.environ.get('CONFIRMATION_PIVOT_CANDLES', '1'))  # Number of Bearish/Bullish Candles After Pivot to Confirm It

    confirmation_candles = 4 # Number of Candles Below Span B To Confirm A Valid Range (Zero And One Means No Confirmation)
    close_confirmation_range = True # If True, Close of Candle Should Break Range
    divergence_confirmation = False # If True, CPD needs divergence confirmation too

    # Determines whether to continuously send the CPD signal regardless of its freshness.
    # If set to True, the same CPD signal will be sent multiple times until it becomes invalid.
    send_repetitive_signal = False

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 70

    # Plot Length
    plot_candle_count = 30

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
            'minimum_lines': {'color': 'aqua'},
        }
    }

    telegram_plot_config_short = {
        'main_plot': {
            'tenkan_sen': {'color': 'orange'},
            'kijun_sen': {'color': 'blue'},
            'leading_senkou_span_b': {'color': 'red'},
            'maximum_lines': {'color': 'aqua'},
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

        # Valid Signals
        dataframe['valid_signal'] = np.nan

        ############## Long Signals ##############
        break_range_src_long = dataframe['close'] if self.close_confirmation_range else dataframe['high']

        # Valid Ranges
        dataframe['long_ranges'] = np.where(break_range_src_long < dataframe['leading_senkou_span_b'], 1, np.nan)
        labels_long, num_features_long = label(dataframe['long_ranges'] == 1)
        counts_long = sum(dataframe['long_ranges'] == 1, labels_long, range(num_features_long + 1))
        dataframe.loc[counts_long[labels_long] < self.confirmation_candles, 'long_ranges'] = np.nan

        # Minimum Lines
        dataframe.loc[dataframe['long_ranges'] == 1, 'minimum_lines'] = dataframe.groupby(labels_long)['low'].transform('min')
        last_min_indices = dataframe.groupby(labels_long)['low'].idxmin().values[-1]

        dataframe['long_target_price_entry'] = np.nan

        group_label = labels_long[last_min_indices]

        group_indices = dataframe[(labels_long == group_label) & (dataframe['long_ranges'] == 1)].index
        if len(group_indices) > 0:
            if self.custom_methods.confirm_long_pivot(dataframe, last_min_indices,
                                                      confirm_window_size=self.confirmation_pivot_candles,
                                                      confirm_by_divergence=self.divergence_confirmation,
                                                      send_repetitive_signal=self.send_repetitive_signal):

                last_index = group_indices[-1]
                dataframe.loc[last_index, 'valid_signal'] = 1

        ############## Long Signals ##############

        ############## Short Signals ##############
        break_range_src_short = dataframe['close'] if self.close_confirmation_range else dataframe['low']

        # Valid Ranges
        dataframe['short_ranges'] = np.where(break_range_src_short > dataframe['leading_senkou_span_b'], 1, np.nan)
        labels_short, num_features_short = label(dataframe['short_ranges'] == 1)
        counts_short = sum(dataframe['short_ranges'] == 1, labels_short, range(num_features_short + 1))
        dataframe.loc[counts_short[labels_short] < self.confirmation_candles, 'short_ranges'] = np.nan

        # Maximum Lines
        dataframe.loc[dataframe['short_ranges'] == 1, 'maximum_lines'] = dataframe.groupby(labels_short)[
            'high'].transform('max')
        last_max_indices = dataframe.groupby(labels_short)['high'].idxmax().values[-1]

        dataframe['short_target_price_entry'] = np.nan

        group_label = labels_short[last_max_indices]

        group_indices = dataframe[(labels_short == group_label) & (dataframe['short_ranges'] == 1)].index
        if len(group_indices) > 0:
            if self.custom_methods.confirm_short_pivot(dataframe, last_max_indices,
                                                       confirm_window_size=self.confirmation_pivot_candles,
                                                       confirm_by_divergence=self.divergence_confirmation,
                                                       send_repetitive_signal=self.send_repetitive_signal):
                last_index = group_indices[-1]
                dataframe.loc[last_index, 'valid_signal'] = -1

        ############## Short Signals ##############

        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the entry signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with entry columns populated
        """
        dataframe.loc[dataframe['valid_signal'] == 1,
            'enter_long'] = 1
        if dataframe['enter_long'].iloc[-1] == 1:
            metadata['strategy_name'] = f"{self.__class__.__name__} (Long)"
            metadata['timeframe'] = self.timeframe
            data = dataframe.tail(self.plot_candle_count)

            self.custom_notif.send_custom_message(self.dp, data, metadata,
                                                  plot_config=self.telegram_plot_config_long,
                                                  markers=None)

        dataframe.loc[dataframe['valid_signal'] == -1,
            'enter_short'] = 1
        if dataframe['enter_short'].iloc[-1] == 1:
            metadata['strategy_name'] = f"{self.__class__.__name__} (Short)"
            metadata['timeframe'] = self.timeframe
            data = dataframe.tail(self.plot_candle_count)

            self.custom_notif.send_custom_message(self.dp, data, metadata,
                                                  plot_config=self.telegram_plot_config_short,
                                                  markers=None)

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the exit signal for the given dataframe
        :param dataframe: DataFrame
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with exit columns populated
        """

        return dataframe
