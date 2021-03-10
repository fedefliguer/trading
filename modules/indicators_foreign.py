"""
Copyright, Rinat Maksutov, 2017.
License: GNU General Public License
"""

import numpy as np
import pandas as pd

"""
Exponential moving average
Source: http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_averages
Params: 
    data: pandas DataFrame
    period: smoothing period
    column: the name of the column with values for calculating EMA in the 'data' DataFrame
    
Returns:
    copy of 'data' DataFrame with 'ema[period]' column added
"""
def ema(data, period=0, column='<CLOSE>'):
    data['ema' + str(period)] = data[column].ewm(ignore_na=False, min_periods=period, com=period, adjust=True).mean()
    
    return data

"""
Moving Average Convergence/Divergence Oscillator (MACD)
Source: http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_average_convergence_divergence_macd
Params: 
    data: pandas DataFrame
    period_long: the longer period EMA (26 days recommended)
    period_short: the shorter period EMA (12 days recommended)
    period_signal: signal line EMA (9 days recommended)
    column: the name of the column with values for calculating MACD in the 'data' DataFrame
    
Returns:
    copy of 'data' DataFrame with 'macd_val' and 'macd_signal_line' columns added
"""
def macd(data, period_long=26, period_short=12, period_signal=9, column='<CLOSE>'):
    remove_cols = []
    if not 'ema' + str(period_long) in data.columns:
        data = ema(data, period_long)
        remove_cols.append('ema' + str(period_long))

    if not 'ema' + str(period_short) in data.columns:
        data = ema(data, period_short)
        remove_cols.append('ema' + str(period_short))

    data['macd_val'] = data['ema' + str(period_short)] - data['ema' + str(period_long)]
    data['macd_signal_line'] = data['macd_val'].ewm(ignore_na=False, min_periods=0, com=period_signal, adjust=True).mean()

    data = data.drop(remove_cols, axis=1)
        
    return data

"""
Accumulation Distribution 
Source: http://stockcharts.com/school/doku.php?st=accumulation+distribution&id=chart_school:technical_indicators:accumulation_distribution_line
Params: 
    data: pandas DataFrame
    trend_periods: the over which to calculate AD
    open_col: the name of the OPEN values column
	high_col: the name of the HIGH values column
	low_col: the name of the LOW values column
	close_col: the name of the CLOSE values column
	vol_col: the name of the VOL values column
    
Returns:
    copy of 'data' DataFrame with 'acc_dist' and 'acc_dist_ema[trend_periods]' columns added
"""
def acc_dist(data, trend_periods=21, open_col='<OPEN>', high_col='<HIGH>', low_col='<LOW>', close_col='<CLOSE>', vol_col='<VOL>'):
    for index, row in data.iterrows():
        if row[high_col] != row[low_col]:
            ac = ((row[close_col] - row[low_col]) - (row[high_col] - row[close_col])) / (row[high_col] - row[low_col]) * row[vol_col]
        else:
            ac = 0
        data.at[index,'acc_dist']=ac
    data['acc_dist_ema' + str(trend_periods)] = data['acc_dist'].ewm(ignore_na=False, min_periods=0, com=trend_periods, adjust=True).mean()
    
    return data

"""
On Balance Volume (OBV)
Source: http://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:on_balance_volume_obv
Params: 
    data: pandas DataFrame
    trend_periods: the over which to calculate OBV
	close_col: the name of the CLOSE values column
	vol_col: the name of the VOL values column
    
Returns:
    copy of 'data' DataFrame with 'obv' and 'obv_ema[trend_periods]' columns added
"""
def on_balance_volume(data, trend_periods=21, close_col='<CLOSE>', vol_col='<VOL>'):
    for index, row in data.iterrows():
        if index > 0:
            last_obv = data.at[index - 1, 'obv']
            if row[close_col] > data.at[index - 1, close_col]:
                current_obv = last_obv + row[vol_col]
            elif row[close_col] < data.at[index - 1, close_col]:
                current_obv = last_obv - row[vol_col]
            else:
                current_obv = last_obv
        else:
            last_obv = 0
            current_obv = row[vol_col]
        data.at[index,'obv']=current_obv

    data['obv_ema' + str(trend_periods)] = data['obv'].ewm(ignore_na=False, min_periods=0, com=trend_periods, adjust=True).mean()
    
    return data

"""
Price-volume trend (PVT) (sometimes volume-price trend)
Source: https://en.wikipedia.org/wiki/Volume%E2%80%93price_trend
Params: 
    data: pandas DataFrame
    trend_periods: the over which to calculate PVT
	close_col: the name of the CLOSE values column
	vol_col: the name of the VOL values columna
    
Returns:
    copy of 'data' DataFrame with 'pvt' and 'pvt_ema[trend_periods]' columns added
"""
def price_volume_trend(data, trend_periods=21, close_col='<CLOSE>', vol_col='<VOL>'):
    for index, row in data.iterrows():
        if index > 0:
            last_val = data.at[index - 1, 'pvt']
            last_close = data.at[index - 1, close_col]
            today_close = row[close_col]
            today_vol = row[vol_col]
            current_val = last_val + (today_vol * (today_close - last_close) / last_close)
        else:
            current_val = row[vol_col]

        data.at[index,'pvt']=current_val

    data['pvt_ema' + str(trend_periods)] = data['pvt'].ewm(ignore_na=False, min_periods=0, com=trend_periods, adjust=True).mean()
        
    return data

"""
Average true range (ATR)
Source: https://en.wikipedia.org/wiki/Average_true_range
Params: 
    data: pandas DataFrame
    trend_periods: the over which to calculate ATR
    open_col: the name of the OPEN values column
	high_col: the name of the HIGH values column
	low_col: the name of the LOW values column
	close_col: the name of the CLOSE values column
	vol_col: the name of the VOL values column
	drop_tr: whether to drop the True Range values column from the resulting DataFrame
    
Returns:
    copy of 'data' DataFrame with 'atr' (and 'true_range' if 'drop_tr' == True) column(s) added
"""
def average_true_range(data, trend_periods=14, open_col='<OPEN>', high_col='<HIGH>', low_col='<LOW>', close_col='<CLOSE>', drop_tr = True):
    for index, row in data.iterrows():
        prices = [row[high_col], row[low_col], row[close_col], row[open_col]]
        if index > 0:
            val1 = np.amax(prices) - np.amin(prices)
            val2 = abs(np.amax(prices) - data.at[index - 1, close_col])
            val3 = abs(np.amin(prices) - data.at[index - 1, close_col])
            true_range = np.amax([val1, val2, val3])

        else:
            true_range = np.amax(prices) - np.amin(prices)

        data.at[index,'true_range']=true_range
    data['atr'] = data['true_range'].ewm(ignore_na=False, min_periods=0, com=trend_periods, adjust=True).mean()
    if drop_tr:
        data = data.drop(['true_range'], axis=1)
        
    return data



"""
Bollinger Bands
Source: https://en.wikipedia.org/wiki/Bollinger_Bands
Params: 
    data: pandas DataFrame
    trend_periods: the over which to calculate BB
	close_col: the name of the CLOSE values column
    
Returns:
    copy of 'data' DataFrame with 'bol_bands_middle', 'bol_bands_upper' and 'bol_bands_lower' columns added
"""
def bollinger_bands(data, trend_periods=20, close_col='<CLOSE>'):

    data['bol_bands_middle'] = data[close_col].ewm(ignore_na=False, min_periods=0, com=trend_periods, adjust=True).mean()
    for index, row in data.iterrows():

        s = data[close_col].iloc[index - trend_periods: index]
        sums = 0
        middle_band = data.at[index, 'bol_bands_middle']
        for e in s:
            sums += np.square(e - middle_band)

        std = np.sqrt(sums / trend_periods)
        d = 2
        upper_band = middle_band + (d * std)
        lower_band = middle_band - (d * std)
	
        data.at[index,'bol_bands_upper']=upper_band
        data.at[index,'bol_bands_lower']=lower_band

    return data

