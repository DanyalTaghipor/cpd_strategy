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
from scipy.ndimage import label, sum
from shared.custom_classes import CustomSender


# This class is a sample. Feel free to customize it.
class CPD(IStrategy):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.custom_notif = CustomSender()
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
    timeframe = '1m'

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

    confirmation_pivot_candles = 2  # Number of Bearish/Bullish Candles After Pivot to Confirm It

    confirmation_candles = 5 # Number of Candles Below Span B To Confirm A Valid Range (Zero And One Means No Confirmation)
    close_confirmation_range = True # If True, Close of Candle Should Break Range

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

    telegram_plot_config = {
        'main_plot': {
            'tenkan_sen': {'color': 'orange'},
            'kijun_sen': {'color': 'blue'},
            'leading_senkou_span_b': {'color': 'red'},
            'minimum_lines': {'color': 'aqua'},
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

    def confirm_long_pivot(self, df_data, index, confirm_window_size):
        """
        Confirm if the given index in a dataframe qualifies as a long pivot based on candle direction and kijun_sen values.

        Parameters
        ----------
        df_data : DataFrame
            The dataframe containing historical market data. Expected to have ohlcv and ichi columns.
        index : int
            The index in the dataframe to check for a long pivot.
        confirm_window_size : int
            The size of the window after the given index to include in the analysis.

        Returns
        -------
        bool
            Returns True if the conditions for a long pivot are satisfied, else False.

        Notes
        -----
        A long pivot is confirmed if:
        1. All candles in the window after the index are bullish.
        2. All 'kijun_sen' values in the window are the same.
        """

        end_index = index + confirm_window_size

        if end_index > len(df_data) - 1:
            return False

        below_base_confirm_data = df_data.loc[index + 1:]

        all_highs_lower = (below_base_confirm_data['high'] < below_base_confirm_data['kijun_sen']).all()

        if not all_highs_lower:
            return False

        piv_confirm_data = below_base_confirm_data.loc[:end_index]

        piv_confirm_data['candle direction'] = 'Bullish'
        piv_confirm_data.loc[piv_confirm_data['open'] > piv_confirm_data['close'], 'candle direction'] = 'Bearish'

        all_bullish = (piv_confirm_data['candle direction'] == 'Bullish').all()

        is_all_base_same = piv_confirm_data['kijun_sen'].nunique() == 1

        is_valid = all_bullish and is_all_base_same

        return is_valid

    def ichimoku(self, dataframe, conversion_line_period=9, base_line_periods=26,
                 laggin_span=52, displacement=26):
        """
        Ichimoku cloud indicator
        Note: Do not use chikou_span for backtesting.
            It looks into the future, is not printed by most charting platforms.
            It is only useful for visual analysis
        :param dataframe: Dataframe containing OHLCV data
        :param conversion_line_period: Conversion line Period (defaults to 9)
        :param base_line_periods: Base line Periods (defaults to 26)
        :param laggin_span: Lagging span period
        :param displacement: Displacement (shift) - defaults to 26
        :return: Dict containing the following keys:
            tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, leading_senkou_span_a,
            leading_senkou_span_b, chikou_span, cloud_green, cloud_red
        """

        tenkan_sen = (dataframe['high'].rolling(window=conversion_line_period).max()
                      + dataframe['low'].rolling(window=conversion_line_period).min()) / 2

        kijun_sen = (dataframe['high'].rolling(window=base_line_periods).max()
                     + dataframe['low'].rolling(window=base_line_periods).min()) / 2

        senkou_span_a = (tenkan_sen + kijun_sen) / 2

        senkou_span_b = (dataframe['high'].rolling(window=laggin_span).max()
                                 + dataframe['low'].rolling(window=laggin_span).min()) / 2

        leading_senkou_span_a = senkou_span_a.shift(displacement)

        leading_senkou_span_b = senkou_span_b.shift(displacement)


        chikou_span = dataframe['close'].shift(-displacement)

        cloud_green = (senkou_span_a > senkou_span_b)
        cloud_red = (senkou_span_b > senkou_span_a)

        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'leading_senkou_span_a': leading_senkou_span_a,
            'leading_senkou_span_b': leading_senkou_span_b,
            'chikou_span': chikou_span,
            'cloud_green': cloud_green,
            'cloud_red': cloud_red,
        }


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
        ichi_ = self.ichimoku(dataframe=dataframe,
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
        break_range_src_long = dataframe['close'] if self.close_confirmation_range else dataframe['low']

        # Valid Ranges
        dataframe['long_ranges'] = np.where(break_range_src_long < dataframe['leading_senkou_span_b'], 1, np.nan)
        labels_long, num_features_long = label(dataframe['long_ranges'] == 1)
        counts_long = sum(dataframe['long_ranges'] == 1, labels_long, range(num_features_long + 1))
        dataframe.loc[counts_long[labels_long] < self.confirmation_candles, 'long_ranges'] = np.nan

        # Minimum Lines
        dataframe.loc[dataframe['long_ranges'] == 1, 'minimum_lines'] = dataframe.groupby(labels_long)['low'].transform('min')
        last_min_indices = dataframe.groupby(labels_long)['low'].idxmin().values[-1]

        # Limit Prices
        dataframe['valid_signal'] = np.nan
        dataframe['long_target_price_entry'] = np.nan

        group_label = labels_long[last_min_indices]

        group_indices = dataframe[(labels_long == group_label) & (dataframe['long_ranges'] == 1)].index
        if len(group_indices) > 0:
            if self.confirm_long_pivot(dataframe, last_min_indices,
                                       confirm_window_size=self.confirmation_pivot_candles):

                last_index = group_indices[-1]
                dataframe.loc[last_index, 'valid_signal'] = 1

        ############## Long Signals ##############

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
            metadata['strategy_name'] = self.__class__.__name__
            data = dataframe.tail(self.plot_candle_count)

            self.custom_notif.send_custom_message(self.dp, data, metadata,
                                                  plot_config=self.telegram_plot_config,
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
