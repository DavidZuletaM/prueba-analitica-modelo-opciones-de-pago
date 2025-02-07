import pandas as pd

# Creación de los Dataframes
df_trtest = pd.read_csv("data/prueba_op_base_pivot_var_rpta_alt_enmascarado_trtest.csv")
df_prob = pd.read_csv("data/prueba_op_probabilidad_oblig_base_hist_enmascarado_completa.csv")
df_hist_pagos = pd.read_csv("data/prueba_op_maestra_cuotas_pagos_mes_hist_enmascarado_completa.csv")
df_mcd = pd.read_csv("data/prueba_op_master_customer_data_enmascarado_completa.csv")

# Creación de llaves para realizar el cruce entre tablas
df_trtest["key"] = (
    df_trtest["nit_enmascarado"].astype(str) + "_" + df_trtest["num_oblig_enmascarado"].astype(str)
)

df_hist_pagos["key"] = (
    df_hist_pagos["nit_enmascarado"].astype(str) + "_" + df_hist_pagos["num_oblig_enmascarado"].astype(str)
)

df_prob["key"] = (
    df_prob["nit_enmascarado"].astype(str) + "_" + df_prob["num_oblig_enmascarado"].astype(str)
)

# Feature Engineering

# Base histórica de pagos del cliente
df1_hist_pagos = (
    df_hist_pagos.groupby("key")
    .agg({
        "valor_cuota_mes":"mean",
        "pago_total":["sum","count","mean"],
        "porc_pago":"mean",
        "fecha_pago_minima":"min",
        "fecha_pago_maxima":"max"
    })
    .reset_index()
)
df1_hist_pagos.columns = [
    "key",
    "promedio_valor_cuota_mes",
    "pago_total",
    "conteo_total_pagos",
    "promedio_pago_mes",
    "promedio_porc_pago_cuota_mes",
    "primer_fecha_pago",
    "ult_fecha_pago"
]

df2_hist_pagos = (
    df_hist_pagos.pivot_table(
        index='key', 
        columns='ajustes_banco', 
        values= 'nit_enmascarado', 
        aggfunc= 'count', 
        fill_value=0
    )
    .reset_index()
)
df2_hist_pagos.columns = [
    "key",
    "tipo_ajuste_ajustes",
    "tipo_ajuste_sin_ajustes",
    "tipo_ajuste_rediferidos"
]

#Base resultados modelos analíticos para cobranza

df1_prob=(
    df_prob.groupby("key").agg({
        "prob_propension":"mean",
        "prob_alrt_temprana":"mean",
        "prob_auto_cura":"mean",
        "lote": lambda x: x.mode().iloc[0]
    })
    .reset_index()
)
df1_prob.columns=[
    "key",
    "prob_prom_propension_mes",
    "prob_prom_alrt_temprana",
    "prob_prom_auto_cura",
    "lote_moda"
]

#Creación del Dataset para entrenar y testear el modelo de Machine Learning

df_resultado=(
    df_trtest
    .merge(
        df_mcd[["nit_enmascarado","edad_cli","estado_civil","tipo_vivienda","personas_dependientes",
                   "nivel_academico","ocup", "declarante", "total_ing", "tot_activos", "tot_pasivos", 
                   "f_vinc", "egresos_mes", "tot_patrimonio"]
        ], 
        on="nit_enmascarado", 
        how="left"
    )
    .merge(
        df1_hist_pagos, 
        on="key", 
        how="left"
    )
    .merge(
        df2_hist_pagos, 
        on="key", 
        how="left"
    )
    .merge(
        df1_prob, 
        on="key", 
        how="left"
    )
)