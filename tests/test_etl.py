"""Tests del ETL. Usan unittest (los ejecuta tanto `pytest` como `python -m unittest`)."""
import copy
import sqlite3
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from demanda.config import PROJECT_ROOT, load_config
from demanda.etl.extract import extract
from demanda.etl.load import connect, init_schema, load
from demanda.etl.pipeline import run_etl
from demanda.etl.transform import ETIQUETAS, transform
from demanda.etl.validate import ETLValidationError, assert_valid, validate

CFG = load_config()
SCHEMA = PROJECT_ROOT / "src" / "demanda" / "db" / "schema.sql"
CSV_REAL = PROJECT_ROOT / "data" / "raw" / "demanda_electricidad_original_mensual1.csv"


def make_raw(n=48, con_sectores_desde=12, con_dist_desde=24, seed=0) -> pd.DataFrame:
    """CSV crudo sintético con la misma forma que el real (sectores y distribuidoras con nulos iniciales)."""
    rng = np.random.default_rng(seed)
    fechas = pd.date_range("2010-01-01", periods=n, freq="MS")
    mes = fechas.month.to_numpy()
    total = 1000 + 5 * np.arange(n) + 100 * np.cos(2 * np.pi * (mes - 1) / 12) + rng.normal(0, 5, n)
    df = pd.DataFrame({"indice_tiempo": fechas, "demanda_total": total})
    reparto = np.array([0.5, 0.35, 0.15])
    for i, c in enumerate(CFG["etl"]["columnas_sectoriales"]):
        df[c] = total * reparto[i]
        df.loc[: con_sectores_desde - 1, c] = np.nan
    df["temperatura_promedio"] = 18 + 8 * np.cos(2 * np.pi * (mes - 1) / 12)
    df["potencia_maxima"] = total * 2
    for c in ("dist_a", "dist_b"):
        df[c] = total * 0.3
        df.loc[: con_dist_desde - 1, c] = np.nan
    return df


class TestValidate(unittest.TestCase):
    def test_datos_validos(self):
        self.assertTrue(validate(make_raw(), CFG).ok)

    def test_fecha_duplicada(self):
        df = make_raw()
        df.loc[5, "indice_tiempo"] = df.loc[4, "indice_tiempo"]
        self.assertFalse(validate(df, CFG).ok)

    def test_mes_faltante(self):
        df = make_raw().drop(index=10)
        self.assertTrue(any("faltantes" in e for e in validate(df, CFG).errores))

    def test_columna_obligatoria_ausente(self):
        df = make_raw().drop(columns=["potencia_maxima"])
        self.assertTrue(any("ausentes" in e for e in validate(df, CFG).errores))

    def test_negativos(self):
        df = make_raw()
        df.loc[3, "demanda_total"] = -1
        self.assertFalse(validate(df, CFG).ok)

    def test_temperatura_fuera_de_rango(self):
        df = make_raw()
        df.loc[3, "temperatura_promedio"] = 99
        self.assertFalse(validate(df, CFG).ok)

    def test_sectores_no_suman_el_total(self):
        df = make_raw()
        df.loc[30, "demanda_residencial"] *= 1.5
        self.assertTrue(any("no coincide" in e for e in validate(df, CFG).errores))

    def test_sectores_parcialmente_nulos(self):
        df = make_raw()
        df.loc[30, "grandes_usuarios"] = np.nan
        self.assertFalse(validate(df, CFG).ok)

    def test_nulos_esperados_son_advertencia_no_error(self):
        rep = validate(make_raw(), CFG)
        self.assertTrue(any("sectorial" in a for a in rep.advertencias))
        self.assertTrue(any("Distribuidoras" in a for a in rep.advertencias))

    def test_assert_valid_lanza(self):
        df = make_raw()
        df.loc[3, "demanda_total"] = -1
        with self.assertRaises(ETLValidationError):
            assert_valid(df, CFG)


class TestTransform(unittest.TestCase):
    def setUp(self):
        self.datos, self.larga, self.info = transform(make_raw(), CFG)

    def test_una_fila_por_mes_y_etiquetas_validas(self):
        self.assertEqual(len(self.datos), 48)
        self.assertTrue(set(self.datos["etiqueta"]) <= set(ETIQUETAS))

    def test_calendario(self):
        enero = self.datos[self.datos["mes"] == 1].iloc[0]
        self.assertEqual(enero["estacion"], "Verano")
        self.assertAlmostEqual(self.datos["mes_sin"].pow(2).add(self.datos["mes_cos"].pow(2)).mean(), 1.0)

    def test_participaciones_suman_uno_y_nulos_se_conservan(self):
        con = self.datos[self.datos["tiene_sectores"] == 1]
        sumas = con[["part_residencial", "part_comercio_industria", "part_grandes_usuarios"]].sum(axis=1)
        np.testing.assert_allclose(sumas, 1.0)
        self.assertEqual(int((self.datos["tiene_sectores"] == 0).sum()), 12)
        self.assertTrue(self.datos.loc[self.datos["tiene_sectores"] == 0, "demanda_residencial"].isna().all())

    def test_split_cronologico(self):
        train = self.datos[self.datos["split"] == "train"]["fecha"]
        test = self.datos[self.datos["split"] == "test"]["fecha"]
        self.assertLess(train.max(), test.min())
        self.assertEqual(len(test), round(48 * CFG["etiqueta"]["fraccion_test"]))

    def test_umbrales_solo_con_train(self):
        """Sin fuga: cambiar los valores del período de test NO modifica los umbrales."""
        raw = make_raw()
        _, _, info_a = transform(raw, CFG)
        raw2 = raw.copy()
        n_test = info_a["n_test"]
        raw2.loc[raw2.index[-n_test:], "demanda_total"] *= 50
        raw2.loc[raw2.index[-n_test:], CFG["etl"]["columnas_sectoriales"]] *= 50
        cfg_global = copy.deepcopy(CFG)
        cfg_global["etiqueta"]["metodo"] = "percentil_global"
        _, _, g1 = transform(raw, cfg_global)
        _, _, g2 = transform(raw2, cfg_global)
        self.assertEqual(g1["p_alta"], g2["p_alta"])
        self.assertEqual(g1["p_critica"], g2["p_critica"])

    def test_metodo_desconocido(self):
        cfg = copy.deepcopy(CFG)
        cfg["etiqueta"]["metodo"] = "inventado"
        with self.assertRaises(ValueError):
            transform(make_raw(), cfg)

    def test_distribuidoras_formato_largo_sin_nulos(self):
        self.assertEqual(len(self.larga), (48 - 24) * 2)
        self.assertFalse(self.larga["demanda"].isna().any())
        self.assertEqual(set(self.larga["distribuidora"]), {"dist_a", "dist_b"})

    def test_columnas_prohibidas_existen_en_tabla(self):
        """Las columnas marcadas como prohibidas para features deben existir (para poder excluirlas)."""
        for c in CFG["modelado"]["columnas_prohibidas_como_feature"]:
            self.assertIn(c, self.datos.columns)


class TestLoad(unittest.TestCase):
    def _cargar(self, conn):
        datos, larga, info = transform(make_raw(), CFG)
        aud = {"archivo": "x.csv", "sha256": "0" * 64, "filas_leidas": 48, "nulos": {}, "umbrales": info,
               "advertencias": [], "config": {"semilla": 42}}
        return load(conn, datos, larga, aud)

    def test_carga_idempotente_y_nulos_como_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = connect(Path(tmp) / "t.db")
            init_schema(conn, SCHEMA)
            self._cargar(conn)
            self._cargar(conn)  # segunda corrida: no duplica
            cur = conn.cursor()
            self.assertEqual(cur.execute("SELECT COUNT(*) FROM datos_limpios").fetchone()[0], 48)
            self.assertEqual(cur.execute("SELECT COUNT(*) FROM demanda_distribuidora").fetchone()[0], 48)
            self.assertEqual(cur.execute("SELECT COUNT(*) FROM etl_auditoria").fetchone()[0], 2)
            self.assertEqual(
                cur.execute("SELECT COUNT(*) FROM datos_limpios WHERE demanda_residencial IS NULL").fetchone()[0], 12)
            conn.close()

    def test_esquema_incluye_las_tablas_requeridas(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = connect(Path(tmp) / "t.db")
            init_schema(conn, SCHEMA)
            tablas = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertTrue({"datos_limpios", "predicciones", "metricas_modelo", "config_modelo"} <= tablas)
            conn.close()

    def test_rollback_si_falla_la_carga(self):
        with tempfile.TemporaryDirectory() as tmp:
            conn = connect(Path(tmp) / "t.db")
            init_schema(conn, SCHEMA)
            self._cargar(conn)
            datos, larga, info = transform(make_raw(), CFG)
            datos.loc[0, "etiqueta"] = "Inválida"  # viola el CHECK de la tabla
            aud = {"archivo": "x", "sha256": "0", "filas_leidas": 48, "nulos": {}, "umbrales": info,
                   "advertencias": [], "config": {}}
            with self.assertRaises(sqlite3.IntegrityError):
                load(conn, datos, larga, aud)
            n = conn.execute("SELECT COUNT(*) FROM datos_limpios").fetchone()[0]
            self.assertEqual(n, 48)  # la carga anterior sigue intacta
            conn.close()


@unittest.skipUnless(CSV_REAL.exists(), "CSV real no disponible")
class TestCsvReal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.tmp.name) / "real.db"
        cls.res = run_etl(db_path=str(cls.db))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_conteos(self):
        self.assertEqual(self.res["filas_datos_limpios"], 308)
        self.assertEqual(self.res["filas_distribuidoras"], 150 * 23)

    def test_sectores_desde_2005(self):
        conn = sqlite3.connect(self.db)
        minimo = conn.execute("SELECT MIN(fecha) FROM datos_limpios WHERE tiene_sectores = 1").fetchone()[0]
        self.assertEqual(minimo, CFG["modelado"]["desde_fecha_sectores"])
        conn.close()

    def test_las_tres_clases_en_train(self):
        conn = sqlite3.connect(self.db)
        clases = {r[0] for r in conn.execute("SELECT DISTINCT etiqueta FROM datos_limpios WHERE split='train'")}
        self.assertEqual(clases, set(ETIQUETAS))
        conn.close()

    def test_fechas_extraidas(self):
        df = extract(CSV_REAL, CFG)
        self.assertEqual(len(df), 308)
        self.assertEqual(df["indice_tiempo"].min().date().isoformat(), "2001-01-01")


if __name__ == "__main__":
    unittest.main()
