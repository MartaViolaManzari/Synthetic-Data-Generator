import logging
import time
from typing import Callable, Optional
import pandas as pd
from vertexai.generative_models import GenerativeModel
from google.api_core import exceptions as api_exceptions

logger = logging.getLogger(__name__)



# CHIAMATA GEMINI IN BATCH

def call_gemini_batch(
    prompts: list[str], 
    model_name: str = "gemini-2.5-flash", 
    max_retries: int = 3, 
    delay: int = 5,
    default_value: str = "N/A"
) -> list[str]:
    """
    Esegue una chiamata batch a Gemini con retry e fallback.
    """
    for attempt in range(1, max_retries + 1):
        try:
            model = GenerativeModel(model_name, generation_config={"temperature": 1.7})
    
            # Prompt concatenato
            full_prompt = (
                "Stai generando valori per una colonna di una tabella CSV. "
                "Ogni blocco numerato rappresenta una richiesta. "
                "Rispondi con un solo valore per ciascuna richiesta, numerato da 1 a N. "
                "Tutti i valori devono essere diversi tra loro: evita ripetizioni, varia lo stile e il contenuto. "
                "Non aggiungere spiegazioni, introduzioni, commenti, punto elenco, né testo extra. "
                "Rispondi solo con i valori richiesti, uno per riga, nel formato:\n"
                "1. <valore>\n2. <valore>\n ... \n\n"
                "Ecco le richieste:\n\n"
                + "\n".join([f"{i+1}. {p}" for i, p in enumerate(prompts)])
            )

            response = model.generate_content(full_prompt)
            logger.info(f"Risposta Gemini batch ricevuta (tentativo {attempt})")
            
            # Split delle risposte
            raw_text = response.text.strip()
            answers = []

            for line in raw_text.splitlines():
                if line.strip() and line[0].isdigit():
                    parts = line.split(".", 1)
                    if len(parts) == 2:
                        answers.append(parts[1].strip())

            if not answers:
                logger.warning("Nessuna risposta valida estratta dal testo Gemini.")
                answers = [default_value] * len(prompts)

            if len(answers) < len(prompts):
                logger.warning(f"Batch incompleto: atteso {len(prompts)}, ricevuto {len(answers)}")
                answers += [default_value] * (len(prompts) - len(answers))

            return answers

        except (api_exceptions.GoogleAPIError, Exception) as e:
            logger.warning(f"Errore Gemini batch (tentativo {attempt}): {e}")
            time.sleep(delay)

    logger.error("Gemini ha fallito dopo i retry.")
    return [default_value] * len(prompts)



# RIEMPIMENTO COLONNA CON GEMINI

def riempi_colonna_gemini(
    df: pd.DataFrame,
    colonna_target: str,
    prompt_template: str,
    colonne_temp: Optional[dict[str, Callable[[pd.Series], any]]] = None,
    batch_size: int = 10,
    rimuovi_temp: bool = True,
    validatore: Optional[Callable[[list[str]], list]] = None,
    default_value: str = "N/A"   
) -> pd.DataFrame:
    """
    Modifica una colonna esistente nel DataFrame usando Gemini e un prompt generativo.

    Args:
        df: DataFrame da modificare
        colonna_target: nome della colonna da sovrascrivere
        prompt_template: stringa con placeholder da usare per generare i prompt
        colonne_temp: dizionario {nome_colonna: funzione(row) -> valore} per colonne di supporto
        batch_size: numero di righe per chiamata batch
        rimuovi_temp: se True, rimuove le colonne temporanee dopo la generazione
        validatore: funzione che prende una lista di stringhe e restituisce una lista di valori validati
        default_value: valore da inserire in caso di fallback

    Returns:
        DataFrame aggiornato
    """

    # aggiunta colonne temporanee
    if colonne_temp:
        try:
            for nome, funzione in colonne_temp.items():
                # applico la funzione riga per riga
                df[nome] = df.apply(funzione, axis=1)
        except Exception as e:
            logger.error(f"Errore durante la creazione delle colonne temporanee: {e}")
            raise  

    results = []
    # generazione batch
    batch_failures = 0

    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        try:
            prompts = [prompt_template.format(**row) for _, row in batch.iterrows()]
        except Exception as e:
            logger.error(f"Errore nella costruzione del prompt per il batch {i}-{i+batch_size}: {e}")
            raise

        try:
            responses = call_gemini_batch(prompts, default_value=default_value)
        except Exception as e:
            logger.error(f"Errore nella chiamata Gemini per il batch {i}-{i+batch_size}: {e}")
            responses = [default_value] * len(batch)
        
        # se Gemini ha restituito meno risposte
        if len(responses) != len(batch):
            logger.warning(f"Batch incompleto: atteso {len(batch)}, ricevuto{len(responses)}")
            responses += [default_value] * (len(batch) - len(responses))

        # validazione dei risultati
        if validatore:
            try:
                responses = validatore(responses)
            except Exception as e:
                logger.error(f"Errore nel validatore per il batch{i}-{i+batch_size}: {e}")
                responses = [None] * len(batch)

        # interruzione se tutto è fallito
        if all(r == default_value for r in responses):
            batch_failures += 1
            if batch_failures >= 3:
                logger.error(f"Troppi batch falliti. Interrompo.")
                break

        # aggiungo le risposte alla lista results
        results.extend(responses)

    # scrittura colonna modificata
    if len(results) != len(df):
        logger.error(f"Mismatch: risultati ({len(results)}) vs righe DataFrame ({len(df)}).")
        raise ValueError("La lunghezza di 'results' non corrisponde al numero di righe del DataFrame.")
    
    df[colonna_target] = results

    # pulizia colonne temporanee
    if rimuovi_temp and colonne_temp:
        df.drop(columns=list(colonne_temp.keys()), inplace=True)
    
    logger.info(f"Generazione completata: {len(results)} valori generati per '{colonna_target}'")
    return df