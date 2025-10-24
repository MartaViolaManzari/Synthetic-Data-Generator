import json
import logging
import time
from typing import List
import pandas as pd
from vertexai.generative_models import GenerativeModel
from google.api_core import exceptions as api_exceptions

logger = logging.getLogger(__name__)



# CALL GEMINI PER SELEZIONE TAG DA LISTA

def call_gemini_tag_selection(
    prompts: List[str], 
    model_name: str = "gemini-2.5-flash", 
    max_retries: int = 3, 
    delay: int = 5,
    batch_size: int = 25
) -> List[List[str]]:
    """
    Chiamata batch a Gemini per selezionare tag da una lista predefinita.
    Divide automaticamente i prompt in sottobatch per evitare timeout.

    Args:
        prompts: lista di prompt, ciascuno con tag disponibili e descrizione del corso o risorsa
        model_name: nome del modello Gemini da usare
        max_retries: numero massimo di tentativi in caso di errore
        delay: ritardo tra i retry
        batch_size: numero massimo di prompt per batch

    Returns:
        Lista di liste di tag scelti (stringhe), uno per ciascun prompt
    """
    all_results: List[List[str]] = []
    total = len(prompts)
    logger.info(f"Avvio Gemini tag selection su {total} prompt con batch da {batch_size}")

    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        sub_prompts = prompts[start:end]
        logger.info(f"Elaborazione batch {start}-{end-1} ({len(sub_prompts)} prompt)")

        for attempt in range(1, max_retries + 1):
            try:
                model = GenerativeModel(model_name, generation_config={"temperature": 0.7})
                full_prompt = (
                    "Per ciascuna richiesta, scegli solo tra i tag elencati. "
                    "Non inventare nuovi tag. Rispondi con una lista di tag separati da virgola, senza commenti.\n\n"
                    "Ecco le richieste:\n\n"
                    + "\n".join([f"{i+1}. {p}" for i, p in enumerate(sub_prompts)])
                )

                logger.info(f"Invio batch {start}-{end-1} a Gemini (tentativo {attempt})")
                response = model.generate_content(full_prompt)
                raw_text = response.text.strip()
                logger.debug("\n--- RAW TEXT DA GEMINI ---\n" + raw_text)

                parsed: List[List[str]] = []            
                for line in raw_text.splitlines():
                    line = line.strip()
                    if not line:
                        continue

                    # cerca numerazione tipo "1. ..." o "1:" o "1 -"
                    if line[0].isdigit():
                        parts = line.split(".", 1)
                        if len(parts) != 2:
                            parts = line.split(":", 1)
                        if len(parts) != 2:
                            parts = line.split("-", 1)
                        if len(parts) == 2:
                            tag_text = parts[1].strip()
                            tag_list = [tag.strip() for tag in tag_text.split(",") if tag.strip()]
                            parsed.append(tag_list)
                    else:
                        # fallback: riga singola con tag separati da virgola
                        tag_list = [tag.strip() for tag in line.split(",") if tag.strip()]
                        if tag_list:
                            parsed.append(tag_list)

                if not parsed:
                    logger.warning(f"Nessuna risposta valida estratta per batch {start}-{end-1}")
                    parsed = [[] for _ in sub_prompts]

                if len(parsed) < len(sub_prompts):
                    logger.warning(f"Batch incompleto: atteso {len(sub_prompts)}, ricevuto {len(parsed)}")
                    parsed += [[] for _ in range(len(sub_prompts) - len(parsed))]

                all_results.extend(parsed)
                break   # esce dal retry loop se va tutto bene


            except (api_exceptions.GoogleAPIError, Exception) as e:
                logger.warning(f"Errore Gemini batch {start}-{end-1} (tentativo {attempt}): {e}")
                time.sleep(delay)
            
        else:
            logger.error(f"Gemini ha fallito per batch {start}-{end-1} dopo {max_retries} tentativi")
            all_results.extend([[] for _ in sub_prompts])

    logger.info(f"Completato: {len(all_results)} risposte totali su {total} prompt")
    return all_results



# GENERAZIONE PROMPT PER RISORSE

def genera_prompt_risorsa(df_resource: pd.DataFrame) -> List[str]:
    """
    Genera i prompt da inviare a Gemini per ciascuna risorsa.
    """
    prompts: List[str] = []
    for _, row in df_resource.iterrows():
        name = row.get("name", "")
        intro = str(row.get("intro", ""))[:300] # tronca a max 300 caratteri
        
        prompt = (
            f"Titolo: '{name}'. Descrizione: '{intro}'. "
            f"Genera 1-3 tag sintetici e descrittivi, separati da virgola. "
            f"I tag devono essere brevi, utili per un sistema di raccomandazione, senza ripetizioni né commenti."    
        )
        prompts.append(prompt)
    return prompts



# CALL GEMINI PER GENERAZIONE TAG LIBERA

def call_gemini_tag_generation(
    prompts: List[str], 
    model_name: str = "gemini-2.5-flash", 
    batch_size: int = 25
) -> List[List[str]]:
    """
    Genera tag per le risorse usando Gemini, con output JSON per garantire allineamento.
    Ogni batch restituisce una lista di liste di tag, una per ciascun prompt. 
    """
    all_results: List[List[str]] = []
    logger.info(f"Avvio generazione tag liberi per {len(prompts)} risorse")

    model = GenerativeModel(model_name, generation_config={"temperature": 0.3})

    for start in range(0, len(prompts), batch_size):
        sub_prompts = prompts[start:start+batch_size]
        logger.info(f"Batch {start}-{start+len(sub_prompts)-1}")

        # prompt JSON-based
        full_prompt = (
            "Genera da 1 a 3 tag sintetici per ciascuna risorsa. "
            "Rispondi SOLO in formato JSON valido, senza testo aggiuntivo, "
            "come lista di liste di stringhe.\n"
            "Esempio di output valido:\n"
            '[["tag1", "tag2"], ["tag3"], ["tag4", "tag5", "tag6]]\n\n'
            "Ora genera i tag per queste risorse:\n"
        )
        for i, p in enumerate(sub_prompts, start=1):
            full_prompt += f"{i}. {p}\n"

        try:
            response = model.generate_content(full_prompt)
            raw_text = response.text.strip()
            logger.debug(f"\n--- RAW TEXT BATCH ({start}) ---\n{raw_text}")

            parsed_batch = None

            # primo tentativo: parsing diretto
            try:
                parsed_batch = json.loads(raw_text)
            except Exception:
                if "[" in raw_text and "]" in raw_text:
                    candidate = raw_text[raw_text.find("["): raw_text.rfind("]")+1]
                    try:
                        parsed_batch = json.loads(candidate)
                    except Exception as e:
                        logger.error(f"Parsing JSON fallito nel batch {start} anche dopo fallback: {e}")
                else:
                    logger.error(f"Nessun JSON rilevato nel batch {start}")

            # se ancora None => placeholder
            if parsed_batch is None:
                parsed_batch = [[] for _ in sub_prompts]

            # sanity check: deve essere una lista di liste
            if not isinstance(parsed_batch, list):
                parsed_batch = [[] for _ in sub_prompts]
            else:
                parsed_batch = [
                    [str(tag).strip() for tag in tags][:3] if isinstance(tags, list) else []
                    for tags in parsed_batch
                ]

            # forzatura dell'allineamento
            if len(parsed_batch) < len(sub_prompts):
                # aggiunta di placeholder vuoti
                parsed_batch.extend([[] for _ in range(len(sub_prompts) - len(parsed_batch))])
            elif len(parsed_batch) > len(sub_prompts):
                # troncare l'eccesso
                parsed_batch = parsed_batch[:len(sub_prompts)]

            # aggiunta dei risultati del batch a all_results
            all_results.extend(parsed_batch)

            # debug: salva batch problematici
            if any(len(tags) == 0 for tags in parsed_batch):
                with open(f"debug_batch_{start}.txt", "w", encoding="utf-8") as f:
                    f.write(raw_text)

        except Exception as e:
            logger.error(f"Errore batch {start}: {e}")
            all_results += [[] for _ in sub_prompts]

    assert len(all_results) == len(prompts), "Mismatch tra numero di prompt e risultati!"
    return all_results



