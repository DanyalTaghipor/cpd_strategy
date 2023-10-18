import json
import numpy as np
from pandas import DataFrame


class CustomSender:

    def send_custom_message(self, dp, dataframe: DataFrame, metadata, plot_config, markers):
        msg = {}
        ohlcv_keys = ["open", "high", "low", "close", "volume"]

        msg['ohlcv_data'] = {ohlcv_key: dataframe[ohlcv_key].tolist() for ohlcv_key in ohlcv_keys}
        plot_data = {}
        if plot_config:
            for key, attributes in plot_config['main_plot'].items():
                plot_data[key] = {
                    'data': dataframe[key].tolist(),
                    'color': attributes['color']
                }
        msg['main_plot_data'] = plot_data
        msg['metadata'] = metadata
        msg['markers'] = markers
        dp.send_msg(json.dumps(msg))

class CustomMethods:

    def confirm_long_pivot(self, df_data, index, confirm_window_size, confirm_by_divergence=True):
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
        :param confirm_by_divergence:
        """

        end_index = index + confirm_window_size

        if end_index > len(df_data) - 1:
            return False

        below_base_confirm_data = df_data.loc[index:]

        all_highs_lower = (below_base_confirm_data['high'] < below_base_confirm_data['kijun_sen']).all()

        if not all_highs_lower:
            return False

        piv_confirm_data = below_base_confirm_data.loc[:end_index]

        piv_confirm_data['candle direction'] = 'Bullish'
        piv_confirm_data.loc[piv_confirm_data['open'] > piv_confirm_data['close'], 'candle direction'] = 'Bearish'

        all_bullish = (piv_confirm_data['candle direction'] == 'Bullish').all()

        is_all_base_same = piv_confirm_data['kijun_sen'].nunique() == 1

        bearish_divergence = True

        if confirm_by_divergence:
            price_slope = np.polyfit(range(len(piv_confirm_data)), piv_confirm_data["close"].values, 1)[0]
            conversion_line_slope = np.polyfit(range(len(piv_confirm_data)), piv_confirm_data["tenkan_sen"].values, 1)[0]

            # # Detect bullish divergence
            # bullish_divergence = price_slope < 0 and conversion_line_slope > 0

            bearish_divergence = price_slope > 0 > conversion_line_slope

        is_valid = all_bullish and is_all_base_same and bearish_divergence

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
