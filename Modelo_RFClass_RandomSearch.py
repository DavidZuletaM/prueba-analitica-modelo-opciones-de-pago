import pandas as pd
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, PolynomialFeatures, FunctionTransformer, RobustScaler
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.compose import make_column_selector, make_column_transformer
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.feature_selection import SelectFromModel

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

# Base resultados modelos analíticos para cobranza

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

# Base master customer data
df1_mcd = df_mcd.sort_values(
    by=["year", "month", "ingestion_day"],
    ascending=[False, False, False]
)
df2_mcd = df1_mcd.drop_duplicates(subset="nit_enmascarado", keep="first")
df2_mcd.reset_index(drop=True, inplace=True)

# Creación del Dataset para entrenar y testear el modelo de Machine Learning
df_resultado=(
    df_trtest
    .merge(
        df2_mcd[["nit_enmascarado","edad_cli","estado_civil","tipo_vivienda","personas_dependientes",
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
).reset_index()

#Definición de variable respuesta
y = df_resultado["var_rpta_alt"]
X = df_resultado.copy()
X.drop("var_rpta_alt", axis=1, inplace=True)

#Preparación de los conjuntos de datos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

# Función para reemplazar valores infinitos por NaN
def replace_infinite(X):
    if isinstance(X, pd.DataFrame):
        num_cols = X.select_dtypes(include=[np.number]).columns
        X[num_cols] = X[num_cols].replace([np.inf, -np.inf], np.nan)
    else:
        X = np.where(np.isinf(X), np.nan, X)
    return X

# Función para detección de outliers
def detect_outliers(X):
    iso = IsolationForest(contamination=0.05, random_state=0)
    outliers = iso.fit_predict(X)
    return outliers.reshape(-1, 1)


# Pipeline

n_pipeline = Pipeline(
    steps=[
        ("replace_infinite", FunctionTransformer(replace_infinite)),
        (
            "column_transformer",
            make_column_transformer(
                (
                    KNNImputer(n_neighbors=3),
                    make_column_selector(dtype_include=[np.number]), 
                ),
                (
                    SimpleImputer(strategy="most_frequent"),
                    make_column_selector(dtype_include=object), 
                ),
                (
                    FunctionTransformer(detect_outliers),
                    make_column_selector(dtype_include=[np.number]),   
                ),
                (
                    OrdinalEncoder(categories="auto",
                                   dtype=np.float64, 
                                   handle_unknown="use_encoded_value",
                                   unknown_value=-1
                    ),
                    make_column_selector(dtype_include=object), 
                ),
                (
                    PolynomialFeatures(interaction_only=True, include_bias=False),
                    make_column_selector(dtype_include=[np.number]),    
                ),
                (
                    RobustScaler(),
                    make_column_selector(dtype_include=[np.number]),    
                ),
                remainder='passthrough',
            ),
        ),
        (
            "feature_selection",
            SelectFromModel(RandomForestClassifier(n_estimators=100, random_state=0)),
        ),
        (
            "RFClassifier",
            RandomForestClassifier(random_state= 0),
        ),
    ],
    verbose=False,
)

# Creación de grilla de hiperparámetros
param_grid = {
    'RFClassifier__n_estimators':np.arange(10,50,10),
    'RFClassifier__criterion':['gini','entropy','log_loss'],
    'RFClassifier__max_depth': [3,5,10]    
}

# Busqueda de los hiperparámetros
RF_randomSearch = RandomizedSearchCV(
    n_pipeline,
    param_grid
)

# Entrenamiento del modelo
RF_randomSearch.fit(X_train,y_train)

# Generar resultados de predicciones
y_pred = RF_randomSearch.best_estimator_.predict(X_test)


# Cálculo de Métricas
print(f"Accuracy: {metrics.accuracy_score(y_test,y_pred)}")
print(f"Precission: {metrics.precision_score(y_test,y_pred)}")
print(f"Recall: {metrics.recall_score(y_test,y_pred)}")
print(f"F1: {metrics.f1_score(y_test,y_pred)}")