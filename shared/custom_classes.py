import json
import numpy as np
from pandas import DataFrame


class CustomSender:

    def send_custom_message(self, dp, dataframe: DataFrame, metadata, plot_config, markers):
        msg = {}
        ohlcv_keys = ["open", "high", "low", "close", "volume"]

        msg['ohlcv_data'] = {ohlcv_key: dataframe[ohlcv_key].tolist() for ohlcv_key in ohlcv_keys}
        main_plot_data = {}
        sub_plot_data = {}
        if plot_config:
            for key, attributes in plot_config['main_plot'].items():
                main_plot_data[key] = {
                    'data': dataframe[key].tolist(),
                    'color': attributes['color']
                }
            if 'sub_plot' in plot_config:
                for key, attributes in plot_config['sub_plot'].items():
                    sub_plot_data[key] = {
                        'data': dataframe[key].tolist(),
                        'color': attributes['color']
                    }
        msg['main_plot_data'] = main_plot_data
        msg['sub_plot_data'] = sub_plot_data
        msg['metadata'] = metadata
        msg['markers'] = markers
        dp.send_msg(json.dumps(msg))

class CustomMethods:

    def find_pivot_lows(self, df,
                        lowest_pivot_range,
                        confirmation_pivot_candles,
                        confirmation_pivot_candles_type,
                        diff_between_maximum_and_twenty_six_point,
                        close_above_conversion,
                        divergence_confirmation,
                        entry_price_type,
                        entry_base_distance,
                        tp_base_check_point_type):
        """
        Find pivot lows in a DataFrame with OHLC data and determine the entry signal.
        """
        # Calculate pivot lows
        pivot_lows = (df['low'] < df['low'].shift(1)) & (df['low'] < df['low'].shift(-1))
        df['pivot_lows'] = np.where(pivot_lows, df['low'], np.nan)

        # Filter pivot lows based on lowest_pivot_range
        if lowest_pivot_range > 0:
            rolling_min = df['low'].shift(1).rolling(window=lowest_pivot_range, min_periods=1).min()
            df['pivot_lows'] = np.where(df['pivot_lows'] <= rolling_min, df['pivot_lows'], np.nan)

        df['long_signal'] = np.nan

        look_ahead_num = confirmation_pivot_candles if confirmation_pivot_candles > 0 else 1

        # Filter based on additional conditions
        for i in df[df['pivot_lows'].notna()].index:
            entry_price = df[str.lower(entry_price_type)].iloc[i + look_ahead_num]

            # Confirmation check
            if confirmation_pivot_candles > 0 and i + confirmation_pivot_candles < len(df):
                confirmation_cond = self._check_confirmation(df=df, pivot_index=i,
                                                             signal_index=i + confirmation_pivot_candles,
                                                             confirmation_pivot_candles_type=confirmation_pivot_candles_type)
                if not confirmation_cond:
                    continue

            # Check diff_between_maximum_and_twenty_six_point
            if diff_between_maximum_and_twenty_six_point > 0 and not self._check_maximum_diff(df=df,
                                                                                              signal_index=i + look_ahead_num,
                                                                                              diff_value=diff_between_maximum_and_twenty_six_point):
                continue

            # Check close_above_conversion
            if close_above_conversion and not self._check_close_above_conversion(df=df,
                                                                                 pivot_index=i,
                                                                                 signal_index=i + look_ahead_num):
                continue

            # Check divergence
            if divergence_confirmation and not self._divergence_confirmation(df=df, pivot_index=i):
                continue

            # Check entry base distance
            if entry_base_distance > 0 and not self._check_entry_base_distance(df=df,
                                                                               pivot_index=i,
                                                                               signal_index=i + look_ahead_num,
                                                                               entry_base_distance=entry_base_distance,
                                                                               entry_price=entry_price,
                                                                               tp_base_check_point_type=tp_base_check_point_type):
                continue

            df.at[i + look_ahead_num, 'long_signal'] = entry_price

        return df

    def _check_confirmation(self, df, pivot_index, signal_index, confirmation_pivot_candles_type):
        confirmation_candles = df.iloc[pivot_index + 1:signal_index + 1]
        if confirmation_pivot_candles_type == 'bullish':
            return all(confirmation_candles['close'] > confirmation_candles['open'])
        else:
            return all(confirmation_candles['close'] > df.at[pivot_index, 'close'])

    def _check_maximum_diff(self, df, signal_index, diff_value):
        start_index = max(0, signal_index - 26)
        highest_index = df['high'][start_index:signal_index + 1].idxmax()
        return abs(start_index - highest_index) >= diff_value

    def _check_close_above_conversion(self, df, pivot_index, signal_index):
        return df['close'].iloc[signal_index] > df['tenkan_sen'].iloc[pivot_index]

    def _divergence_confirmation(self, df, pivot_index):
        next_index = pivot_index + 1
        return df['tenkan_sen'].iloc[next_index] < df['tenkan_sen'].iloc[pivot_index]

    def _check_entry_base_distance(self, df, pivot_index, signal_index, entry_base_distance, entry_price, tp_base_check_point_type):
        baseline_value = df['kijun_sen'].iloc[pivot_index if tp_base_check_point_type == 'minimum' else signal_index]
        percent_diff = ((baseline_value - entry_price) / entry_price) * 100
        return percent_diff >= entry_base_distance

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
