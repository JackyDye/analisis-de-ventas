import os
import zipfile
from pathlib import Path
from sqlalchemy import create_engine
import pandas as pd

# Paths
ROOT_DIR = Path(__file__).parent
DATA_DIR = ROOT_DIR / "data" / "archive"
DB_PATH = ROOT_DIR / "data" / "olist.db"
KAGGLE_JSON = ROOT_DIR / "kaggle.json"

def configurar_kaggle():
    """Copia kaggle.json al lugar que espera la librería."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(exist_ok=True)
    dest = kaggle_dir / "kaggle.json"
    if not dest.exists():
        import shutil
        shutil.copy(KAGGLE_JSON, dest)
        dest.chmod(0o600)
        print("kaggle.json configurado")
    else:
        print("kaggle.json ya existe")

def descargar_dataset():
    """Descarga el dataset de Olist desde Kaggle."""
    if DATA_DIR.exists() and any(DATA_DIR.iterdir()):
        print("Dataset ya descargado")
        return

    print("Descargando dataset de Kaggle...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    os.system(
        f'kaggle datasets download -d olistbr/brazilian-ecommerce -p "{DATA_DIR}" --unzip'
    )
    print("Dataset descargado")

def crear_base_datos():
    """Importa los CSVs a SQLite."""
    if DB_PATH.exists():
        print("Base de datos ya existe")
        return

    print("Creando base de datos SQLite...")
    engine = create_engine(f"sqlite:///{DB_PATH}")

    tablas = {
        "orders": "olist_orders_dataset.csv",
        "order_items": "olist_order_items_dataset.csv",
        "order_payments": "olist_order_payments_dataset.csv",
        "order_reviews": "olist_order_reviews_dataset.csv",
        "customers": "olist_customers_dataset.csv",
        "products": "olist_products_dataset.csv",
        "sellers": "olist_sellers_dataset.csv",
        "product_category_translation": "product_category_name_translation.csv",
        "geolocation": "olist_geolocation_dataset.csv",
    }

    for tabla, archivo in tablas.items():
        df = pd.read_csv(DATA_DIR / archivo)
        df.to_sql(tabla, engine, if_exists="replace", index=False)
        print(f"  ✓ {tabla}: {len(df):,} filas")

    engine.dispose()
    print("Base de datos creada")

def eliminar_csvs():
    """Elimina los CSVs descargados para liberar espacio."""
    import shutil
    if DATA_DIR.exists():
        shutil.rmtree(DATA_DIR)
        print("CSVs eliminados")

if __name__ == "__main__":
    configurar_kaggle()
    descargar_dataset()
    crear_base_datos()
    eliminar_csvs()
    print("\nSetup completo. Ya podés abrir el notebook.")