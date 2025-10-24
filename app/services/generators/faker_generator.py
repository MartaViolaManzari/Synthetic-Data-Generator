import pandas as pd
import random
import logging
from faker import Faker
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)

faker = Faker("it_IT")



# LOOKUP FUNZIONI FAKER

def faker_lookup(tipo: str) -> Callable[[], Any]:
    """
    Restituisce una funzione Faker in base al tipo richiesto.

    Args:
        tipo: stringa come 'email', 'name', 'address', 'text', ecc.

    Returns:
        Funzione Faker corrispondente
    """
    lookup = {
        "stringa": lambda: faker.word(),
        "intero": lambda: faker.random_int(min=0, max=100),
        "booleano": lambda: faker.boolean(),
        "email": lambda: faker.email(),
        "nome": lambda: faker.first_name(),
        "cognome": lambda: faker.last_name(),
        "username": lambda: faker.user_name(),
        "password": lambda: "$2y$" + faker.sha256(raw_output=False)[3:],
        "telefono": lambda: faker.phone_number(),
        "istituzione": lambda: faker.company(),
        "dipartimento": lambda: faker.bs(),

        "indirizzo": lambda: faker.address(),
        "città": lambda: faker.city(),
        "paese": lambda: faker.country(),
        "ip": lambda: faker.ipv4(),
        "timestamp": lambda: int(faker.date_time_between(start_date="-5y", end_date="now").timestamp())
    }
    if tipo not in lookup:
        logger.warning(f"Tipo Faker '{tipo}' non riconosciuto, restituisco NA.")
        return lambda: pd.NA
    return lookup[tipo]



# FUNZIONI BASE

def riempi_colonna_faker(df: pd.DataFrame, colonna: str, tipo: str = "stringa") -> pd.DataFrame:
    """
    Riempie una colonna con valori generati da Faker in base al tipo specificato.
    """
    generatore = faker_lookup(tipo)
    df[colonna] = [generatore() for _ in range(len(df))]
    return df

def riempi_colonna_null(df: pd.DataFrame, colonna: str) -> pd.DataFrame:
    """
    Imposta la colonna specificata a valori nulli (pandas NA).
    """
    df[colonna] = pd.NA
    return df

def riempi_colonna_default(df: pd.DataFrame, colonna: str, valore=0) -> pd.DataFrame:
    """
    Imposta la colonna specificata a un valore di default.
    """
    df[colonna] = valore
    return df

def riempi_colonna_lista(df: pd.DataFrame, colonna: str, valori: list) -> pd.DataFrame:
    """
    Riempie la colonna con valori casuali scelti presi da una lista
    """
    df[colonna] = [random.choice(valori) for _ in range(len(df))]
    return df

def riempi_colonna_float_range(
    df: pd.DataFrame, 
    colonna: str, 
    minimo: float, 
    massimo: float, 
    decimali: int = 1
) -> pd.DataFrame:
    """
    Riempie la colonna con float casuali tra minimo e massimo.

    Args:
        df: DataFrame da modificare
        colonna: nome della colonna da riempire
        minimo: valore minimo (incluso)
        massimo: valore massimo (incluso)
        decimali: numero di cifre decimali (default: 1)

    Returns:
        DataFrame aggiornato
    """
    df[colonna] = [round(random.uniform(minimo, massimo), decimali) for _ in range(len(df))]
    return df

# PER RIEMPIRE LE COLONNE RELATIVE AGLI UTENTI
def riempi_utenti_coerenti(df: pd.DataFrame) -> pd.DataFrame:
    """
    Riempie le colonne firstname, lastname, username, email con dati coerenti tra loro.
    """
    utenti = []

    for _ in range(len(df)):
        first = faker.first_name()
        last = faker.last_name()
        username = f"{first.lower()}.{last.lower()}"
        email = f"{username}@example.com"

        utenti.append({
            "firstname": first,
            "lastname": last,
            "username": username,
            "email": email
        })

    df_utenti = pd.DataFrame(utenti)
    for col in df_utenti.columns:
        df[col] = df_utenti[col]

    return df



# RIEMPIMENTO DA SCHEMA

# Mappa funzioni disponibili
FUNZIONI_RIEMPIMENTO: Dict[str, Callable[..., pd.DataFrame]] = {
    "riempi_colonna_faker": riempi_colonna_faker,
    "riempi_colonna_null": riempi_colonna_null,
    "riempi_colonna_default": riempi_colonna_default,
    "riempi_colonna_lista": riempi_colonna_lista,
    "riempi_colonna_float_range": riempi_colonna_float_range,
    "riempi_utenti_coerenti": riempi_utenti_coerenti,
}

def riempi_colonne_da_schema(df: pd.DataFrame, schema: dict) -> pd.DataFrame:
    """
    Riempie più colonne in un DataFrame usando uno schema di configurazione.

    Args:
        df: DataFrame da modificare
        schema: dict con {colonna: {"func": nome_funzione, "args": {...}}}

    Returns:
        DataFrame aggiornato
    """
    for col, config in schema.items():
        func_name = config["func"]
        args = config.get("args", {})
        func = FUNZIONI_RIEMPIMENTO.get(func_name)
        if func:
            df = func(df, col, **args)
        else:
            logger.error(f"Funzione '{func_name}' non trovata per la colonna '{col}'")
    return df
    


















