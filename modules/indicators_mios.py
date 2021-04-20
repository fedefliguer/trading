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
  """Agrega una columna (no relativa a Y) con la proporción que tiene la amplitud del precio."""
  data['amp_std'] = (data[high_col] - data[low_col])/data[close_col]
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
  """Agrega una columna (no relativa a Y) con el volumen en forma estandarizada."""
  mean_vl = data['<VOL>'].mean()
  std_vl = data['<VOL>'].std()
  data['vol_std'] = (data['<VOL>'] - mean_vl)/std_vl
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
def calcula_canalidad_y(data, high_col='<HIGH>', low_col='<LOW>', close_col='<CLOSE>', lista_ventanas = [5, 30, 90, 180]):
  for ventana in lista_ventanas: 
    data['lag_y_1'] = data[close_col].shift(1)
    colname_maxmin = "nu_dias_y_entre_max_min_%s" % (ventana)
    data[colname_maxmin] = np.where((data['lag_y_1'] < data[high_col]) & (data['lag_y_1'] > data[low_col]), 1, 0)
    colname_5pc = "nu_dias_y_entre_5pc_%s" % (ventana)
    data[colname_5pc] = np.where((data['lag_y_1'] < (data[close_col] * 1.05)) & (data['lag_y_1'] > (data[close_col] * 0.95)), 1, 0)
    data = data.drop(['lag_y_1'], axis=1)
    i = 2
    while i <= ventana:
      colname_lag = "lag_y_%s" % (i)
      data[colname_lag] = data[close_col].shift(i)
      data[colname_maxmin] = data[colname_maxmin] + np.where((data[colname_lag] < data[high_col]) & (data[colname_lag] > data[low_col]), 1, 0)
      data[colname_5pc] = data[colname_5pc] + np.where((data[colname_lag] < (data[close_col] * 1.05)) & (data[colname_lag] > (data[close_col] * 0.95)), 1, 0)
      i = i + 1
      data = data.drop([colname_lag], axis=1)
  return data

"""
CANALIDAD DEL HISTOGRAMA MACD
Params: 
    data: pandas DataFrame
    histog_col: the name of the HISTOG values column
    
Returns:
    copy of 'data' DataFrame con columnas de número de días en (5, 30, 90, 180) los que el histograma MACD fue positivo, negativo e igual al del cierre
"""
def calcula_canalidad_histog_macd(data, histog_col='macd_histog', ventanas = [5, 30, 90, 180]):
  for ventana in ventanas:
    i = 1
    data['lag_histog_1'] = data.histog.shift(1)
    colname_nu_1 = "nu_dias_histog_entre_5pc_%s" % (ventana)
    data[colname_nu_1] = np.where((data['lag_histog_1'] < (data.histog * 1.05)) & (data['lag_histog_1'] > (data.histog * 0.95)), 1, 0)

    colname_nu_2 = "nu_dias_histog_positivo_%s" % (ventana)
    data[colname_nu_2] = np.where((data['lag_histog_1']>0), 1, 0)

    colname_nu_3 = "nu_dias_histog_negativo_%s" % (ventana)
    data[colname_nu_3] = np.where((data['lag_histog_1']<0), 1, 0)

    colname_nu_4 = "nu_dias_histog_mismo_signo_%s" % (ventana)
    data[colname_nu_4] = np.where(((data['lag_histog_1']>0) & (data['histog']>0))|((data['lag_histog_1']<0) & (data['histog']<0)), 1, 0)

    data = data.drop(['lag_histog_1'], axis=1)
    i = 2
    while i < (ventana+1):
      colname = "lag_histog_%s" % (i)
      data[colname] = data.histog.shift(i)
      data[colname_nu_1] = data[colname_nu_1] + np.where((data[colname] < (data.histog * 1.50)) & (data[colname] > (data.histog * 0.50)), 1, 0)
      data[colname_nu_2] = data[colname_nu_2] + np.where((data[colname]>0), 1, 0)
      data[colname_nu_3] = data[colname_nu_3] + np.where((data[colname]<0), 1, 0)
      data[colname_nu_4] = data[colname_nu_4] + np.where(((data[colname]>0) & (data['histog']>0))|((data[colname]<0) & (data['histog']<0)), 1, 0)
      i = i + 1
      data = data.drop([colname], axis=1)
  return data

"""
ANALISIS TÉCNICO
Params: 
    data: pandas DataFrame
    lags: días antes y días después que no debe superarlo para considerar que un pico fue real
    close_col: the name of the CLOSE values column
    date_col: the name of the FC values column
    
Returns:
    copy of 'data' DataFrame con columnas de análisis técnico
"""
def calcula_AT_tendencias(data, lags, close_col='<CLOSE>', date_col='<FC>'):
  
  # Construye las columnas para determinar si es un pico
  i = 1
  while i < (lags+1):
      colname = 'p%sb' % (i)                                                  
      data[colname] = round(data[close_col].shift(i),2)
      j = i * -1
      colname = 'p%sf' % (-j)                                                  
      data[colname] = round(data[close_col].shift(j),2)
      i = i + 1

  # Determina si es un pico  
  data['maxb'] = round(data.filter(regex=(".*b")).max(axis=1),2)
  data['maxf']= round(data.filter(regex=(".*f")).max(axis=1),2)
  data['minb'] = round(data.filter(regex=(".*b")).min(axis=1),2)
  data['minf'] = round(data.filter(regex=(".*f")).min(axis=1),2)
  data['T'] = np.where((data[close_col]>data['maxb']) & (data[close_col]>data['maxf']), 1, 0)
  data['P'] = np.where((data[close_col]<data['minb']) & (data[close_col]<data['minf']), 1, 0)

  techos = data[(data['T']==1)].copy()
  techos['m'] = (techos[close_col].shift(1) - techos[close_col])/(techos[date_col].shift(1) - techos[date_col]).dt.days
  techos.name = 'techos'
  pisos = data[(data['P']==1)].copy()
  pisos['m'] = (pisos[close_col].shift(1) - pisos[close_col])/(pisos[date_col].shift(1) - pisos[date_col]).dt.days
  pisos.name = 'pisos'
  data_list = [techos, pisos]

  for data_picos in data_list:  # En cada data (techos y pisos)
    name = data_picos.name
    dias = len(data)
    print(data_picos.name, " - Número de picos: ", data_picos.iloc[1:].shape[0])
    iterrow_actual = 1
    for index, row in data_picos.iloc[1:].iterrows(): # Para cada pico detectado (fila del data) a partir del segundo (porque el primero no tiene anterior, no tiene tendencia)
      print(data_picos.name, ": Desarrollo el pico ", iterrow_actual)
      iterrow_actual = iterrow_actual+1
      y_start = row[close_col]
      pendiente = row['m']
      if (dias < np.where(data[date_col]==row[date_col])[0] + lags):
        continue    
      serie = [] # Crea la serie que va a contener el precio proyectado
      serie = np.append(serie, np.repeat(np.nan, (np.where(data[date_col]==row[date_col])[0] + lags))) # Appendea nulos hasta el día en el que confirmamos que nació una tendencia
      i = np.where(data[date_col]==row[date_col])[0] + lags
      while (i < dias):
        dia = i - (np.where(data[date_col]==row[date_col])[0] + lags)
        serie = np.append(serie, (y_start + pendiente*lags) + pendiente*dia)
        i = i + 1 # Appendea el precio proyectado hasta el final

      colname = '%s_%s_proy' % (name, index)  # Precio proyectado
      data[colname] = serie # Construye la columna de toda la serie

      # Construyo columna con veces en la que el pico fue superado
      colname_pass = '%s_%s_pass' % (name, index) # Pico pasado
      if name == 'techos':
        data[colname_pass] = np.where(data[close_col]>(data[colname])*1.005, 1, 0)
      elif name == 'pisos':
        data[colname_pass] = np.where(data[close_col]<(data[colname])*0.995, 1, 0)
      data[colname_pass] = data[colname_pass].cumsum()

      # Construyo columna con veces en la que el pico fue probado
      colname_prueba = '%s_%s_prueba' % (name, index)  
      data[colname_prueba] = np.where((data[close_col]>data[colname]*0.995)&(data[close_col]<data[colname]*1.005), 1, 0)
      data[colname_prueba] = data[colname_prueba].cumsum()

      # Construyo columna con pendiente del pico
      colname_pendiente = '%s_%s_pendiente' % (name, index)  
      data[colname_pendiente] = row['m']

      # Creo la combinacion y elimino cada uno
      colname_comb = '%s_%s' % (name, index)
      data[colname_comb] = data[[colname, colname_pass, colname_prueba, colname_pendiente]].values.tolist()
      del data[colname]
      del data[colname_pass]
      del data[colname_prueba]
      del data[colname_pendiente]

  # Creo el objeto por cada techo o piso individual
  names_techos = data.filter(regex=("(techos)(.*)")).columns
  names_pisos = data.filter(regex=("(pisos)(.*)")).columns

  print("Filas: ", data.shape[0])
  j = 0
  for index, row in data.iterrows():  # Por cada fila del data original (por cada precio)
    j = j + 1
    if (j % 1000 == 0):
      print("Voy por la fila ", j)

    # Genero las rows vacías con las variables agregadas
    nu_pruebas_techo_vivo_mas_probado = np.nan    
    precio_proyectado_techo_vivo_mas_probado = np.nan
    precio_proyectado_techo_vivo_mas_cercano = np.nan
    precio_proyectado_techo_muerto_mas_cercano = np.nan
    tendencia_techo_vivo_mas_probado = np.nan

    nu_pruebas_piso_vivo_mas_probado = np.nan
    precio_proyectado_piso_vivo_mas_probado = np.nan
    precio_proyectado_piso_vivo_mas_cercano = np.nan
    precio_proyectado_piso_muerto_mas_cercano = np.nan
    tendencia_piso_vivo_mas_probado = np.nan

    # Voy a recorrer cada tendencia proyectada para definir cuáles van, en caso de que corresponda lo asigno a estas variables agregadas

    i = 0
    while i < len(row.index): # Por cada uno de los picos de los que se puede armar tendencia
      if (row.index[i] in names_techos):  # Si es un techo
        if row[i][1]>5: # Si está muerto
          if abs(row[close_col]-row[i][0]) < abs(row[close_col]-precio_proyectado_techo_muerto_mas_cercano) or np.isnan(precio_proyectado_techo_muerto_mas_cercano): # Si está muerto y proyecta precio más cercano que el actual
            precio_proyectado_techo_muerto_mas_cercano = row[i][0]
            
        else: # Si está vivo
          if row[i][2] > nu_pruebas_techo_vivo_mas_probado or (np.isnan(nu_pruebas_techo_vivo_mas_probado) and row[i][2]>0): # Si fue más probado que el actual
            nu_pruebas_techo_vivo_mas_probado = row[i][2]
            precio_proyectado_techo_vivo_mas_probado = row[i][0]
            tendencia_techo_vivo_mas_probado = row[i][3]

          if (np.isnan(precio_proyectado_techo_vivo_mas_cercano)) or (abs(row[close_col]-row[i][0]) < abs(row[close_col]-precio_proyectado_techo_vivo_mas_cercano)): # Si, sin haber muerto, proyecta un techo más alto que el actual
            precio_proyectado_techo_vivo_mas_cercano = row[i][0]

      elif (row.index[i] in names_pisos):
        if row[i][1]>5: # Si está muerto
          if abs(row[close_col]-row[i][0]) < abs(row[close_col]-precio_proyectado_piso_muerto_mas_cercano) or np.isnan(precio_proyectado_piso_muerto_mas_cercano): # Si proyecta precio más cercano que el actual
            precio_proyectado_piso_muerto_mas_cercano = row[i][0]
            
        else: # Si está vivo
          if row[i][2] > nu_pruebas_piso_vivo_mas_probado or (np.isnan(nu_pruebas_piso_vivo_mas_probado) and row[i][2]>0): # Si fue más probado que el actual
            nu_pruebas_piso_vivo_mas_probado = row[i][2]
            precio_proyectado_piso_vivo_mas_probado = row[i][0]
            tendencia_piso_vivo_mas_probado = row[i][3]

          if (np.isnan(precio_proyectado_piso_vivo_mas_cercano)) or (abs(row[close_col]-row[i][0]) < abs(row[close_col]-precio_proyectado_piso_vivo_mas_cercano)): # Si, sin haber muerto, proyecta un techo más alto que el actual
            precio_proyectado_piso_vivo_mas_cercano = row[i][0]
      i = i + 1
        
    data.loc[index,'nu_pruebas_techo_vivo_mas_probado_'f"{lags}"] = nu_pruebas_techo_vivo_mas_probado
    data.loc[index,'precio_proyectado_techo_vivo_mas_probado_'f"{lags}"] = (precio_proyectado_techo_vivo_mas_probado - row[close_col])/row[close_col]
    data.loc[index,'precio_proyectado_techo_vivo_mas_cercano_'f"{lags}"] = (precio_proyectado_techo_vivo_mas_cercano - row[close_col])/row[close_col]
    data.loc[index,'precio_proyectado_techo_muerto_mas_cercano_'f"{lags}"] = (precio_proyectado_techo_muerto_mas_cercano - row[close_col])/row[close_col]
    data.loc[index,'tendencia_techo_vivo_mas_probado_'f"{lags}"] = tendencia_techo_vivo_mas_probado/row[close_col]

    data.loc[index,'nu_pruebas_piso_vivo_mas_probado_'f"{lags}"] = nu_pruebas_piso_vivo_mas_probado
    data.loc[index,'precio_proyectado_piso_vivo_mas_probado_'f"{lags}"] = (precio_proyectado_piso_vivo_mas_probado - row[close_col])/row[close_col]
    data.loc[index,'precio_proyectado_piso_vivo_mas_cercano_'f"{lags}"] = (precio_proyectado_piso_vivo_mas_cercano - row[close_col])/row[close_col]
    data.loc[index,'precio_proyectado_piso_muerto_mas_cercano_'f"{lags}"] = (precio_proyectado_piso_muerto_mas_cercano - row[close_col])/row[close_col]
    data.loc[index,'tendencia_piso_vivo_mas_probado_'f"{lags}"] = tendencia_piso_vivo_mas_probado/row[close_col]

  # Elimino todas las que construí excepto estas
  i = 1
  while i < (lags+1):
      colname = 'p%sb' % (i)                                                  
      data = data.drop(colname, axis=1)
      j = i * -1
      colname = 'p%sf' % (-j)                                                  
      data = data.drop(colname, axis=1)
      i = i + 1

  ultimas_drop = ['maxb', 'maxf', 'minb', 'minf', 'T', 'P']
  data = data.drop(ultimas_drop, axis=1)
  data = data.drop(names_techos, axis=1)
  data = data.drop(names_pisos, axis=1)
  return data
