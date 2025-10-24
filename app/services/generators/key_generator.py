import pandas as pd
import random
import logging
from typing import Optional

logger = logging.getLogger(__name__)


# GENERAZIONE CHIAVI PRIMARIE

def genera_chiavi_primarie(df: pd.DataFrame, numero_righe: int) -> pd.DataFrame:
    """
    Aggiunge un numero specifico di righe con chiavi primarie incrementali a un DataFrame.

    Args:
        df: DataFrame originale
        numero_righe: numero di nuove righe da aggiungere

    Returns:
        DataFrame aggiornato con nuove righe e colonna 'id'
    """
    if "id" in df.columns and pd.api.types.is_numeric_dtype(df["id"]):
        ultimo_id = df["id"].max()
    else:
        ultimo_id = 0
        df["id"] = pd.NA    # crea la colonna se non esiste

    nuovi_id = list(range(ultimo_id + 1, ultimo_id + numero_righe + 1))
    nuove_righe = pd.DataFrame({"id": nuovi_id})

    # aggiunge colonne vuote per compatibilità
    for col in df.columns:
        if col != "id":
            nuove_righe[col] = pd.NA

    df_finale = pd.concat([df, nuove_righe], ignore_index=True)
    return df_finale



# GENERAZIONE CHIAVI ESTERNE

def genera_chiavi_esterne(
    df_dest: pd.DataFrame,
    colonna_destinazione: str,
    df_ref: pd.DataFrame,
    colonna_riferimento: str,
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Popola una colonna con chiavi esterne referenziando un'altra tabella,
    distribuendo le chiavi in modo bilanciato con variazione casuale.

    Args:
        df_dest: DataFrame da modificare
        colonna_destinazione: colonna da riempire (es: "category")
        df_ref: DataFrame di riferimento
        colonna_riferimento: colonna chiave primaria di riferimento
        seed: opzionale, per rendere la generazione riproducibilee

    Returns:
        DataFrame aggiornato
    """
    if seed is not None:
        random.seed(seed)

    chiavi_rif = df_ref[colonna_riferimento].dropna().tolist()
    if not chiavi_rif:
        logger.warning("Nessuna chiave di riferimento trovata")
        return df_dest
    
    random.shuffle(chiavi_rif)

    n_dest = len(df_dest)
    n_ref = len(chiavi_rif)
    df_dest[colonna_destinazione] = pd.NA

    base = n_dest // n_ref
    residue = n_dest % n_ref

    assegnazioni = []
    for chiave in chiavi_rif:
        jitter = random.choice([-1, 0, 1])
        n = max(1, base + jitter)

        if residue > 0:
            n += 1
            residue -= 1

        assegnazioni.extend([chiave] * n)

    assegnazioni = assegnazioni[:n_dest]
    while len(assegnazioni) < n_dest:
        assegnazioni.append(random.choice(chiavi_rif))

    random.shuffle(assegnazioni)
    df_dest[colonna_destinazione] = assegnazioni

    return df_dest