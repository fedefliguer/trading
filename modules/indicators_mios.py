"""
Indicadores FJF
"""

import numpy as np
import pandas as pd

"""
AMPLITUD
Params: 
    data: pandas DataFrame
    high_col: the name of the HIGH values column
    low_col: the name of the LOW values column
    close_col: the name of the CLOSE values column
    
Returns:
    copy of 'data' DataFrame with 'amplitud' column added, relativa al precio de cierre
"""
def calcula_amplitud(data, high_col='<HIGH>', low_col='<LOW>', close_col='<CLOSE>'):
  data['amplitud'] = (data[high_col] - data[low_col])/data[close_col]
  return data

"""
ESTANDARIZACIÓN DEL VOLUMEN
Params: 
    data: pandas DataFrame
    vol_col: the name of the VOLUME values column
    
Returns:
    copy of 'data' DataFrame with 'amplitud' column added
"""
def estandariza_volumen(data, vol_col='<VOL>'):
  mean_vl = data['<VOL>'].mean()
  std_vl = data['<VOL>'].std()
  data['<VOL>'] = (data['<VOL>'] - mean_vl)/std_vl
  return data


"""
CANALIDAD DEL CIERRE
Params: 
    data: pandas DataFrame
    high_col: the name of the HIGH values column
    low_col: the name of the LOW values column
    close_col: the name of the CLOSE values column
    
Returns:
    copy of 'data' DataFrame con columnas de número de días en los que el cierre de Y estuvo entre el máximo y el mínimo de ese día, y número de días en los que el cierre de Y estuvo +-5% del cierre, en los últimos (5, 15, 30, 90, 180)
"""
def calcula_canalidad_y(data, high_col='<HIGH>', low_col='<LOW>', close_col='<CLOSE>'):
  i = 1
  data['lag_y_1'] = data[close_col].shift(1)


  data['nu_dias_y_entre_max_min_5'] = np.where((data['lag_y_1'] < data[high_col]) & (data['lag_y_1'] > data[low_col]), 1, 0)
  data['nu_dias_y_entre_5pc_5'] = np.where((data['lag_y_1'] < (data[close_col] * 1.05)) & (data['lag_y_1'] > (data[close_col] * 0.95)), 1, 0)

  data['nu_dias_y_entre_max_min_15'] = np.where((data['lag_y_1'] < data[high_col]) & (data['lag_y_1'] > data[low_col]), 1, 0)
  data['nu_dias_y_entre_5pc_15'] = np.where((data['lag_y_1'] < (data[close_col] * 1.05)) & (data['lag_y_1'] > (data[close_col] * 0.95)), 1, 0)

  data['nu_dias_y_entre_max_min_30'] = np.where((data['lag_y_1'] < data[high_col]) & (data['lag_y_1'] > data[low_col]), 1, 0)
  data['nu_dias_y_entre_5pc_30'] = np.where((data['lag_y_1'] < (data[close_col] * 1.05)) & (data['lag_y_1'] > (data[close_col] * 0.95)), 1, 0)

  data['nu_dias_y_entre_max_min_90'] = np.where((data['lag_y_1'] < data[high_col]) & (data['lag_y_1'] > data[low_col]), 1, 0)
  data['nu_dias_y_entre_5pc_90'] = np.where((data['lag_y_1'] < (data[close_col] * 1.05)) & (data['lag_y_1'] > (data[close_col] * 0.95)), 1, 0)

  data['nu_dias_y_entre_max_min_180'] = np.where((data['lag_y_1'] < data[high_col]) & (data['lag_y_1'] > data[low_col]), 1, 0)
  data['nu_dias_y_entre_5pc_180'] = np.where((data['lag_y_1'] < (data[close_col] * 1.05)) & (data['lag_y_1'] > (data[close_col] * 0.95)), 1, 0)

  data = data.drop(['lag_y_1'], axis=1)

  i = 2
  while i <= 5:
    colname = "lag_y_%s" % (i)
    data[colname] = data[close_col].shift(i)
    data['nu_dias_y_entre_max_min_5'] = data['nu_dias_y_entre_max_min_5'] + np.where((data[colname] < data[high_col]) & (data[colname] > data[low_col]), 1, 0)
    data['nu_dias_y_entre_5pc_5'] = data['nu_dias_y_entre_5pc_5'] + np.where((data[colname] < (data[close_col] * 1.05)) & (data[colname] > (data[close_col] * 0.95)), 1, 0)
    i = i + 1
    data = data.drop([colname], axis=1)

  i = 2
  while i <= 15:
    colname = "lag_y_%s" % (i)
    data[colname] = data[close_col].shift(i)
    data['nu_dias_y_entre_max_min_15'] = data['nu_dias_y_entre_max_min_15'] + np.where((data[colname] < data[high_col]) & (data[colname] > data[low_col]), 1, 0)
    data['nu_dias_y_entre_5pc_15'] = data['nu_dias_y_entre_5pc_15'] + np.where((data[colname] < (data[close_col] * 1.05)) & (data[colname] > (data[close_col] * 0.95)), 1, 0)
    i = i + 1
    data = data.drop([colname], axis=1)

  i = 2
  while i <= 30:
    colname = "lag_y_%s" % (i)
    data[colname] = data[close_col].shift(i)
    data['nu_dias_y_entre_max_min_30'] = data['nu_dias_y_entre_max_min_30'] + np.where((data[colname] < data[high_col]) & (data[colname] > data[low_col]), 1, 0)
    data['nu_dias_y_entre_5pc_30'] = data['nu_dias_y_entre_5pc_30'] + np.where((data[colname] < (data[close_col] * 1.05)) & (data[colname] > (data[close_col] * 0.95)), 1, 0)
    i = i + 1
    data = data.drop([colname], axis=1)

  i = 2
  while i <= 90:
    colname = "lag_y_%s" % (i)
    data[colname] = data[close_col].shift(i)
    data['nu_dias_y_entre_max_min_90'] = data['nu_dias_y_entre_max_min_90'] + np.where((data[colname] < data[high_col]) & (data[colname] > data[low_col]), 1, 0)
    data['nu_dias_y_entre_5pc_90'] = data['nu_dias_y_entre_5pc_90'] + np.where((data[colname] < (data[close_col] * 1.05)) & (data[colname] > (data[close_col] * 0.95)), 1, 0)
    i = i + 1
    data = data.drop([colname], axis=1)

  i = 2
  while i <= 180:
    colname = "lag_y_%s" % (i)
    data[colname] = data[close_col].shift(i)
    data['nu_dias_y_entre_max_min_180'] = data['nu_dias_y_entre_max_min_180'] + np.where((data[colname] < data[high_col]) & (data[colname] > data[low_col]), 1, 0)
    data['nu_dias_y_entre_5pc_180'] = data['nu_dias_y_entre_5pc_180'] + np.where((data[colname] < (data[close_col] * 1.05)) & (data[colname] > (data[close_col] * 0.95)), 1, 0)
    i = i + 1
    data = data.drop([colname], axis=1)

  return data
