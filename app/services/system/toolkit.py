import os
from app.services.utils.helpers import save_table

def promuovi_output(df, nome_base: str, base_dir: str = "app/data/schema"):
    """
    Sposta un DataFrame validato nella cartella schema.

    Args:
        df: DataFrame da salvare
        nome_base: nome base del file (senza estensione), es: "mdl_user"
        base_dir: directory di destinazione (default: app/data/schema)
    """
    os.makedirs(base_dir, exist_ok=True)
    schema_path = os.path.join(base_dir, f"{nome_base}.csv")
    save_table(df, schema_path.replace(".csv", "")) # save_table aggiunge .csv
    
    print(f"File promosso in: {schema_path}")