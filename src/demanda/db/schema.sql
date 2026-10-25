-- Esquema SQLite del proyecto. Idempotente (CREATE TABLE IF NOT EXISTS).
-- Clave natural: `fecha` (primer día del mes, ISO YYYY-MM-DD). No hay `id` autoincremental,
-- así el ETL se puede volver a correr sin romper las referencias de las predicciones.

-- ===================== TABLA 1: datos de entrada limpios y preprocesados =====================
CREATE TABLE IF NOT EXISTS datos_limpios (
    fecha                    TEXT PRIMARY KEY,
    anio                     INTEGER NOT NULL,
    mes                      INTEGER NOT NULL CHECK (mes BETWEEN 1 AND 12),
    trimestre                INTEGER NOT NULL CHECK (trimestre BETWEEN 1 AND 4),
    estacion                 TEXT    NOT NULL CHECK (estacion IN ('Verano','Otoño','Invierno','Primavera')),
    mes_sin                  REAL    NOT NULL,
    mes_cos                  REAL    NOT NULL,
    demanda_total            REAL    NOT NULL,
    demanda_residencial      REAL,
    comercio_e_industria     REAL,
    grandes_usuarios         REAL,
    part_residencial         REAL,
    part_comercio_industria  REAL,
    part_grandes_usuarios    REAL,
    tiene_sectores           INTEGER NOT NULL CHECK (tiene_sectores IN (0,1)),
    temperatura_promedio     REAL    NOT NULL,
    potencia_maxima          REAL    NOT NULL,
    demanda_ratio_tendencia  REAL,
    etiqueta                 TEXT    NOT NULL CHECK (etiqueta IN ('Normal','Alta','Crítica')),
    split                    TEXT    NOT NULL CHECK (split IN ('train','test'))
);
CREATE INDEX IF NOT EXISTS idx_datos_split ON datos_limpios(split);

-- Extra del ETL: demanda por distribuidora en formato largo (solo existe desde 2014-01).
CREATE TABLE IF NOT EXISTS demanda_distribuidora (
    fecha          TEXT NOT NULL,
    distribuidora  TEXT NOT NULL,
    demanda        REAL NOT NULL,
    PRIMARY KEY (fecha, distribuidora)
);

-- Extra del ETL: auditoría de cada corrida (trazabilidad y calidad de datos).
CREATE TABLE IF NOT EXISTS etl_auditoria (
    etl_run_id             TEXT PRIMARY KEY,
    ejecutado_en           TEXT NOT NULL,
    archivo                TEXT NOT NULL,
    sha256                 TEXT NOT NULL,
    filas_leidas           INTEGER NOT NULL,
    filas_datos_limpios    INTEGER NOT NULL,
    filas_distribuidoras   INTEGER NOT NULL,
    nulos_json             TEXT NOT NULL,
    umbrales_json          TEXT NOT NULL,
    advertencias_json      TEXT NOT NULL,
    config_json            TEXT NOT NULL
);

-- ===================== TABLA 2: resultados del modelo =====================
CREATE TABLE IF NOT EXISTS predicciones (
    run_id        TEXT NOT NULL,
    fecha         TEXT NOT NULL REFERENCES datos_limpios(fecha),
    modelo        TEXT NOT NULL,
    y_real        TEXT NOT NULL,
    y_pred        TEXT NOT NULL,
    prob_normal   REAL,
    prob_alta     REAL,
    prob_critica  REAL,
    PRIMARY KEY (run_id, fecha)
);
CREATE INDEX IF NOT EXISTS idx_pred_modelo ON predicciones(modelo);

CREATE TABLE IF NOT EXISTS metricas_modelo (
    run_id                  TEXT PRIMARY KEY,
    modelo                  TEXT NOT NULL,
    accuracy                REAL NOT NULL,
    precision_macro         REAL NOT NULL,
    recall_macro            REAL NOT NULL,
    f1_macro                REAL NOT NULL,
    precision_normal        REAL, recall_normal  REAL, f1_normal  REAL,
    precision_alta          REAL, recall_alta    REAL, f1_alta    REAL,
    precision_critica       REAL, recall_critica REAL, f1_critica REAL,
    matriz_confusion        TEXT NOT NULL,          -- JSON, orden Normal/Alta/Crítica
    cv_best_score           REAL,
    tiempo_entrenamiento_s  REAL,
    n_train                 INTEGER,
    n_test                  INTEGER,
    created_at              TEXT NOT NULL
);

-- ===================== TABLA 3 (extra): configuración y parametrización =====================
CREATE TABLE IF NOT EXISTS config_modelo (
    run_id               TEXT PRIMARY KEY,
    modelo               TEXT NOT NULL,
    grid_hiperparametros TEXT NOT NULL,   -- JSON
    mejores_params       TEXT NOT NULL,   -- JSON
    umbrales_etiqueta    TEXT NOT NULL,   -- JSON (metodo, p_alta, p_critica)
    features_usadas      TEXT NOT NULL,   -- JSON (lista)
    semilla              INTEGER NOT NULL,
    cv_folds             INTEGER,
    scoring              TEXT,
    created_at           TEXT NOT NULL
);
