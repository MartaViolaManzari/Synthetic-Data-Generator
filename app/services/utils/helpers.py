import pandas as pd

def load_table(table_path: str) -> pd.DataFrame:
    return pd.read_csv(f"{table_path}.csv")

def save_table(df: pd.DataFrame, table_path: str):
    df.to_csv(f"{table_path}.csv", index=False)

def valida_interi(responses: list[str]) -> list[int | None]:
    risultati = []
    for r in responses:
        try:
            risultati.append(int(r.strip()))
        except (ValueError, TypeError):
            risultati.append(None)
    return risultati

def get_value_by_id(
        df: pd.DataFrame,
        row_id: int,
        column_name: str,
        id_column: str = 'id'
):
    """
    Restituisce il valore di una colonna per una riga identificata da ID.

    Args:
        df: DataFrame da cui estrarre il valore
        row_id: valore dell'id da cercare
        column_name: nome della colonna da restituire
        id_column: nome della colonna ID (default 'id')

    Returns:
        Valore corrispondente o None se non trovato
    """
    match = df[df[id_column] == row_id]
    if not match.empty:
        return match.iloc[0][column_name]
    return None