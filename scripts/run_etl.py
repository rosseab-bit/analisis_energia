"""CLI del ETL:  python scripts/run_etl.py [--reset] [--config config/config.yaml]"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from demanda.etl.pipeline import run_etl  # noqa: E402
from demanda.etl.validate import ETLValidationError  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="ETL: CSV de demanda -> SQLite")
    ap.add_argument("--config", default=None, help="ruta a config.yaml (default: config/config.yaml)")
    ap.add_argument("--reset", action="store_true",
                    help="borra TODAS las tablas (incluye resultados de modelos) antes de cargar")
    args = ap.parse_args()
    try:
        r = run_etl(args.config, reset=args.reset)
    except ETLValidationError as exc:
        print(f"[ETL] DATOS INVÁLIDOS: {exc}", file=sys.stderr)
        return 1
    print(f"[ETL] OK -> {r['base_datos']}")
    print(f"  datos_limpios: {r['filas_datos_limpios']} filas | demanda_distribuidora: {r['filas_distribuidoras']} filas")
    u = r["umbrales"]
    print(f"  etiqueta ({u['metodo']}): P{int(u['q_alta']*100)}={u['p_alta']:.4f}  P{int(u['q_critica']*100)}={u['p_critica']:.4f}")
    print(f"  train={u['n_train']} (hasta {u['ultimo_mes_train']}) | test={u['n_test']}")
    print("  distribución de etiquetas:", json.dumps(r["distribucion_etiquetas"], ensure_ascii=False))
    for a in r["advertencias"]:
        print("  [aviso]", a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
