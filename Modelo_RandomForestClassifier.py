import pandas as pd

df_trtest=pd.read_csv("data/prueba_op_base_pivot_var_rpta_alt_enmascarado_trtest.csv")
df_prob=pd.read_csv("data/prueba_op_probabilidad_oblig_base_hist_enmascarado_completa.csv")
df_hist_pagos=pd.read_csv("data/prueba_op_maestra_cuotas_pagos_mes_hist_enmascarado_completa.csv")
df_mcd=pd.read_csv("data/prueba_op_master_customer_data_enmascarado_completa.csv")

df_hist_pagos["key"] = df_hist_pagos["nit_enmascarado"].astype(str) + "_" + df_hist_pagos["num_oblig_enmascarado"].astype(str)
df_prob["key"] = df_prob["nit_enmascarado"].astype(str) + "_" + df_prob["num_oblig_enmascarado"].astype(str)

#Feature Engineering

#Base histórica de pagos del cliente
df_hist_pagos_valor_cuota_mes=df_hist_pagos.groupby("key").agg({"valor_cuota_mes":"mean"}).reset_index()
df_hist_pagos_valor_cuota_mes.columns=["key","promedio_valor_cuota_mes"]

df_hist_pagos_pago_total=df_hist_pagos.groupby("key").agg({"pago_total":["sum","count","mean"]}).reset_index()
df_hist_pagos_pago_total.columns=["key","pago_total","conteo_total_pagos","promedio_pago_mes"]

df_hist_pagos_porc_pago=df_hist_pagos.groupby("key").agg({"porc_pago":"mean"}).reset_index()
df_hist_pagos_porc_pago.columns=["key","promedio_porc_pago_cuota_mes"]

df_hist_pagos_fecha_pago_min=df_hist_pagos.groupby("key").agg({"fecha_pago_minima":"min"}).reset_index()
df_hist_pagos_fecha_pago_min.columns=["key","primer_fecha_pago"]

df_hist_pagos_fecha_pago_max=df_hist_pagos.groupby("key").agg({"fecha_pago_maxima":"max"}).reset_index()
df_hist_pagos_fecha_pago_max.columns=["key","ult_fecha_pago"]

df_hist_pagos_producto=df_hist_pagos.groupby("key").agg({"producto": "first"}).reset_index()
df_hist_pagos_producto.columns=["key","producto"]

df_hist_pagos_ajustes_banco=df_hist_pagos.pivot_table(index='key', columns='ajustes_banco', values= 'nit_enmascarado', aggfunc= 'count', fill_value=0).reset_index()
df_hist_pagos_ajustes_banco.columns=["Key","tipo_ajuste_ajustes","tipo_ajuste_sin_ajustes","tipo_ajuste_rediferidos"]

#Base resultados modelos analíticos para cobranza


