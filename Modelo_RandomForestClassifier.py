import pandas as pd

df_trtest=pd.read_csv("data/prueba_op_base_pivot_var_rpta_alt_enmascarado_trtest.csv")
df_prob=pd.read_csv("data/prueba_op_probabilidad_oblig_base_hist_enmascarado_completa.csv")
df_hist_pagos=pd.read_csv("data/prueba_op_maestra_cuotas_pagos_mes_hist_enmascarado_completa.csv")
df_mcd=pd.read_csv("data/prueba_op_master_customer_data_enmascarado_completa.csv")

df_hist_pagos["key"] = df_hist_pagos["nit_enmascarado"].astype(str) + "_" + df_hist_pagos["num_oblig_enmascarado"].astype(str)
df_prob["key"] = df_prob["nit_enmascarado"].astype(str) + "_" + df_prob["num_oblig_enmascarado"].astype(str)

#Feature Engineering

#Base histórica de pagos del cliente
df_hist_pagos=df_hist_pagos.groupby("key").agg({"valor_cuota_mes":"mean","pago_total":["sum","count","mean"],"porc_pago":"mean","fecha_pago_minima":"min","fecha_pago_maxima":"max","producto":"first"}).reset_index()
df_hist_pagos.columns=["key","promedio_valor_cuota_mes","pago_total","conteo_total_pagos","promedio_pago_mes","promedio_porc_pago_cuota_mes","primer_fecha_pago","ult_fecha_pago","producto"]

df_hist_pagos_ajustes_banco=df_hist_pagos.pivot_table(index='key', columns='ajustes_banco', values= 'nit_enmascarado', aggfunc= 'count', fill_value=0).reset_index()
df_hist_pagos_ajustes_banco.columns=["Key","tipo_ajuste_ajustes","tipo_ajuste_sin_ajustes","tipo_ajuste_rediferidos"]

#Base resultados modelos analíticos para cobranza

df_prob=df_prob.groupby("key").agg({"prob_propension":"mean","prob_alrt_temprana":"mean","prob_auto_cura":"mean","lote": lambda x: x.mode().iloc[0]}).reset_index()
df_prob.columns=["key","prob_prom_propension_mes","prob_prom_alrt_temprana","prob_prom_auto_cura","lote_moda"]

