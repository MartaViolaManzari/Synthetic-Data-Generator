import json
import logging
import pandas as pd
from typing import Any, List, Tuple
from app.services.utils.helpers import get_value_by_id
from app.services.generators.tag_gemini import call_gemini_tag_selection, genera_prompt_risorsa, call_gemini_tag_generation

logger = logging.getLogger(__name__)



def genera_tabella_tag(json_path: str) -> pd.DataFrame:
    """
    Genera la tabella a partire da un file JSON che mappa categorie a liste di tag.
    Ogni tag è unico e viene associato a un ID incrementale.

    Args:
        json_path: percorso al file JSON con struttura {nome_categoria: [tag1, tag2, ...]}

    Returns:
        DataFrame con colonne: id, name
    """
    with open(json_path, "r", encoding="utf-8") as f:
        categoria_to_tags: dict[str, list[str]] = json.load(f)

    # estrae tutti i tag unici
    tag_unici = sorted(set(tag.strip() for tags in categoria_to_tags.values() for tag in tags))

    # assegna ID incrementali
    df_tag = pd.DataFrame({
        "id": range(1, len(tag_unici) + 1),
        "name": tag_unici
    })

    logger.info(f"Generata tabella tag con {len(df_tag)} record unici.")
    return df_tag



def genera_tabella_category_tag(
    json_path: str, 
    df_categorie: pd.DataFrame, 
    df_tag: pd.DataFrame
) -> pd.DataFrame:
    """
    Genera la tabella category_tag a partire dal file JSON e dai DataFrame delle categorie e dei tag.

    Args:
        json_path: percorso al file JSON con struttura {nome_categoria: [tag1, tag2, ...]}
        df_categorie: DataFrame con almeno le colonne 'id' e 'name' (da mdl_course_categories)
        df_tag: DataFrame con colonne 'id' e 'name' (da tag.csv)

    Returns:
        DataFrame con colonne: id, category_id, tag_id
    """
    with open(json_path, "r", encoding="utf-8") as f:
        categoria_to_tags: dict[str, list[str]] = json.load(f)

    righe = []
    id_counter = 1

    for nome_cat, lista_tag in categoria_to_tags.items():
        # trova l'id della categoria
        match = df_categorie[df_categorie["name"] == nome_cat]
        if match.empty:
            logger.warning(f"Categoria '{nome_cat}' non trovata in mdl_course_categories")
            continue

        category_id = match.iloc[0]["id"]

        for tag in lista_tag:
            tag = tag.strip()
            tag_match = df_tag[df_tag["name"] == tag]
            if tag_match.empty:
                logger.warning(f"Tag '{tag}' non trovato in tag.csv")
                continue

            tag_id = tag_match.iloc[0]["id"]
            righe.append({
                "id": id_counter,
                "category_id": category_id,
                "tag_id": tag_id
            })
            id_counter += 1
    
    df_category_tag = pd.DataFrame(righe)
    logger.info(f"Generata tabella category_tag con {len(df_category_tag)} record.")
    return df_category_tag



def genera_tabella_course_tag(
    df_course: pd.DataFrame, 
    df_category_tag: pd.DataFrame, 
    df_tag: pd.DataFrame
) -> pd.DataFrame:
    """
    Genera un DataFrame course_tag associato a ciascun corso dei tag coerenti con la sua categoria,
    selezionati tramite Gemini.

    Args:
        df_course: DataFrame mdl_course con almeno 'id', 'fullname', 'summary', 'category'
        df_category_tag: DataFrame category_tag con 'category_id', 'tag_id'
        df_tag: DataFrame tag con 'id', 'name'

    Returns:
        DataFrame con colonne: id, course_id, tag_id
    """
    logger.info("Avvio generazione tabella course_tag")
    
    if df_course.empty or df_category_tag.empty or df_tag.empty:
        logger.warning("Uno o più DataFrame di input sono vuoti. Interrompo la generazione.")
        return pd.DataFrame(columns=["id", "course_id", "tag_id"])
    
    tag_map = df_category_tag.groupby("category_id")["tag_id"].apply(list).to_dict()
    tag_lookup = df_tag.set_index("id")["name"].to_dict()

    prompts = []
    course_ids = []

    logger.info(f"Preparazione prompt per {len(df_course)} corsi")

    for idx, course_id in enumerate(df_course["id"]):
        try:  
            category_id = get_value_by_id(df_course, course_id, "category")
            fullname = get_value_by_id(df_course, course_id, "fullname")
            summary = get_value_by_id(df_course, course_id, "summary") or ""
            tag_ids = tag_map.get(category_id, [])

            if not tag_ids or not fullname:
                logger.info(f"Corso {course_id} ignorato: tag_ids vuoti o fullname mancante.")
                continue
            
            tag_names = [tag_lookup[tid] for tid in tag_ids if tid in tag_lookup]
            if not tag_names:
                logger.info(f"Nessun nome tag valido per categoria {category_id} (corso {course_id})")
                continue

            prompt = (
                f"Il corso si intitola '{fullname}' e ha il seguente contenuto: {summary}. "
                f"Analizza il contenuto e seleziona solo i tag pertinenti tra quelli elencati. "
                f"Tag disponibili (non puoi inventarne altri): {', '.join(tag_names)}. "
                f"Restituisci esclusivamente una lista di massimo 7 tag scelti, separati da virgola, "
                f"senza commenti, spiegazioni o aggiunte. Se nessun tag è rilevante, restituisci almeno uno tra quelli più generici."
            )

            prompts.append(prompt)
            course_ids.append(course_id)

            if idx % 50 == 0:
                logger.info(f"Preparati {idx+1}/{len(df_course)} prompt")

        except Exception as e:
            logger.warning(f"Errore durante la preparazione del prompt per corso {course_id}: {e}")
            continue
    
    logger.info(f"Invio {len(prompts)} prompt a Gemini per selezione tag")

    try:
        # chiamata batch a Gemini
        lista_tag_per_corso = call_gemini_tag_selection(prompts)
    except Exception as e:
        logger.error(f"Errore nella chiamata a Gemini: {e}")
        return pd.DataFrame(columns=["id", "course_id", "tag_id"])

    # costruzione righe course_tag
    righe = []
    id_counter = 1

    logger.info("Costruzione righe course_tag")

    for idx, (course_id, tag_list) in enumerate(zip(course_ids, lista_tag_per_corso)):
        if not isinstance(tag_list, list) or not tag_list:
            logger.info(f"Risposta vuota o non valida per corso {course_id}. Assegno fallback.")
            # fallback: assegna il primo tag disponibile per la categoria
            fallback_tag_ids = tag_map.get(get_value_by_id(df_course, course_id, "category"), [])
            for tid in fallback_tag_ids[:1]:    # solo uno
                tag_name = tag_lookup.get(tid)
                if tag_name:
                    tag_list = [tag_name]
                    break
            if not tag_list:
                continue

        # loop che costruisce le righe
        for tag_name in tag_list[:7]:
            # trova il tag_id corrispondente
            match = df_tag[df_tag["name"] == tag_name]
            if match.empty:
                logger.info(f"Tag '{tag_name}' non trovato in df_tag (corso {course_id})")
                continue

            tag_id = match.iloc[0]["id"]
            righe.append({
                "id": id_counter,
                "course_id": course_id,
                "tag_id": tag_id
            })
            id_counter += 1
        
        if idx % 50 == 0:
            logger.info(f"Elaborate {idx+1}/{len(course_ids)} risposte")

    if not righe:
        logger.warning("Nessuna associazione corso-tag generata.")
        return pd.DataFrame(columns=["id", "course_id", "tag_id"])
    
    df_course_tag = pd.DataFrame(righe)
    logger.info(f"Generazione completata: {len(righe)} righe course_tag create")
    return df_course_tag



def aggiorna_tag_e_resource_tag(
    df_tag: pd.DataFrame,
    df_resource: pd.DataFrame,
    lista_tag_per_risorsa: List[List[str]]
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aggiorna tag e resource_tag evitando duplicati.
    Aggiunge nuovi tag se non esistono e crea relazioni risorsa-tag.

    Args:
        df_tag: DataFrame esistente dei tag (colonne: id, name)
        df_resource: DataFrame delle risorse (colonne: id, name, intro)
        lista_tag_per_risorsa: lista di liste di tag generati da Gemini

    Returns:
        Tuple: (df_tag aggiornato, df_resource_tag generato)
    """
    # lookup esistente: nome tag (lowercase) -> id
    tag_lookup = {name.strip().lower(): tid for tid, name in zip(df_tag["id"], df_tag["name"])}
    tag_id_counter = df_tag["id"].max() + 1 if not df_tag.empty else 1
    
    resource_tag_rows = []
    resource_tag_id_counter = 1
    # per evitare duplicati risorsa-tag
    relazioni_esistenti = set()

    for resource_id, tag_list in zip(df_resource["id"], lista_tag_per_risorsa):
        for tag_name in tag_list[:3]:   # massimo 3 tag per risorsa
            
            tag_name_clean = tag_name.strip()
            tag_key = tag_name_clean.lower()

            # verifica se il tag esiste già
            if tag_key in tag_lookup:
                tag_id = tag_lookup[tag_key]
            else:
                # nuovo tag -> aggiungi a df_tag
                tag_id = tag_id_counter
                df_tag = pd.concat(
                    [df_tag, pd.DataFrame([{"id": tag_id, "name": tag_name_clean}])], 
                    ignore_index=True
                )
                tag_lookup[tag_key] = tag_id
                tag_id_counter += 1
                logger.info(f"Creato un nuovo tag '{tag_name_clean}' con id {tag_id}")

            # verifica se la relazione risorsa-tag esiste già
            rel_key = (resource_id, tag_id)
            if rel_key in relazioni_esistenti:
                continue

            resource_tag_rows.append({
                "id": resource_tag_id_counter,
                "resource_id": resource_id,
                "tag_id": tag_id
            })
            relazioni_esistenti.add(rel_key)
            resource_tag_id_counter += 1

    df_resource_tag = pd.DataFrame(resource_tag_rows)
    logger.info(f"Generati {len(df_resource_tag)} collegamenti risorsa-tag")
    
    return df_tag, df_resource_tag


def genera_tabella_resource_tag(
        df_resource: pd.DataFrame,
        df_tag: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Orchestratore per generare tag sintetici per risorse e aggiornare tag e resource_tag.

    Args:
        df_resource: DataFrame delle risorse (colonne: id, name, intro)
        df_tag: DataFrame esistente dei tag (colonne: id, name)

    Returns:
        Tuple: (df_tag aggiornato, df_resource_tag aggiornato)
    """
    logger.info(f"Avvio generazione tag per {len(df_resource)} risorse")

    # genera i prompt
    prompts = genera_prompt_risorsa(df_resource)
    logger.info(f"Generati {len(prompts)} prompt per Gemini")

    # chiama Gemini per generare i tag
    lista_tag_per_risorsa = call_gemini_tag_generation(prompts)
    logger.info(f"Ricevute {len(lista_tag_per_risorsa)} risposte da Gemini")

    # aggiorna tag e resource_tag
    df_tag_nuovo, df_resource_tag = aggiorna_tag_e_resource_tag(
        df_tag, df_resource, lista_tag_per_risorsa
    )

    logger.info(f"Tag totali dopo aggiornamento: {len(df_tag_nuovo)}")
    logger.info(f"Relazioni risorsa-tag generate: {len(df_resource_tag)}")

    return df_tag_nuovo, df_resource_tag