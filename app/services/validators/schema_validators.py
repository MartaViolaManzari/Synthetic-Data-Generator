import pandas as pd
import logging

logger = logging.getLogger(__name__)



# VALIDAZIONE CHIAVI PRIMARIE

def verifica_chiavi_primarie(df: pd.DataFrame) -> bool:
    """
    Verifica che la colonna 'id' contenga chiavi primarie valide:
    - esista
    - non abbia valori nulli
    - sia numerica
    - sia unica
    - sia strettamente crescente
    """
    if "id" not in df.columns:
        logger.error("La colonna 'id' non esiste.")
        return False
    
    if df["id"].isnull().any():
        logger.error("La colonna 'id' contiene valori nulli.")
        return False
    
    id_numeric = pd.to_numeric(df["id"], errors="coerce")
    if id_numeric.isnull().any():
        logger.error("La colonna 'id' contiene valori non numerici.")
        return False
    
    if df["id"].duplicated().any():
        logger.error("La colonna 'id' contiene duplicati.")
        return False
    
    if not df["id"].is_monotonic_increasing:
        logger.error("Gli ID non sono strettamente crescenti.")
        return False

    logger.info("Chiavi primarie valide.")
    return True



# VALIDAZIONE CHIAVI ESTERNE

def verifica_chiavi_esterne(
        df_dest: pd.DataFrame,
        colonna_destinazione: str,
        df_ref: pd.DataFrame,
        colonna_riferimento: str
) -> bool:
    """
    Verifica che tutte le chiavi esterne in df_dest[colonna_destinazione]
    esistano in df_ref[colonna_riferimento]
    """
    if colonna_destinazione not in df_dest.columns:
        logger.error(f"La colonna '{colonna_destinazione}' non esiste nella tabella di destinazione.")
        return False
    
    if colonna_riferimento not in df_ref.columns:
        logger.error(f"La colonna '{colonna_riferimento}' non esiste nella tabella di riferimento.")
        return False
    
    chiavi_dest = df_dest[colonna_destinazione].dropna().unique()
    chiavi_rif = set(df_ref[colonna_riferimento].dropna().unique())

    non_valide = [k for k in chiavi_dest if k not in chiavi_rif]

    if non_valide:
        logger.error(f"Chiavi esterne non valide trovate: {non_valide[:10]}{'...' if len(non_valide) > 10 else ''}")
        return False
    
    logger.info("Tutte le chiavi esterne sono valide.")
    return True



# VALIDAZIONE TABELLA CONTEXT

def verifica_context(df_context, df_course, df_resource) -> bool:
    """
    Verifica la coerenza della tabella mdl_context:
    - ID primari validi
    - contextlevel ammessi (50, 70)
    - instanceid coerenti con le tabelle referenziate
    """
    if not verifica_chiavi_primarie(df_context):
        logging.error("Chiavi primarie non valide in mdl_context")
        return False
    
    livelli_validi = {50, 70}
    livelli_presenti = set(df_context["contextlevel"].dropna().unique())
    if not livelli_presenti.issubset(livelli_validi):
        logging.error(f"Livelli di contesto non validi: {livelli_presenti - livelli_validi}")
        return False
    
    id_course = set(df_course["id"].dropna().unique())
    id_resource = set(df_resource["id"].dropna().unique())

    errori = []
    for _, row in df_context.iterrows():
        if row["contextlevel"] == 50 and row["instanceid"] not in id_course:
            errori.append(row["instanceid"])
        elif row["contextlevel"] == 70 and row["instanceid"] not in id_resource:
            errori.append(row["instanceid"])

    if errori:
        logging.error(f"instanceid non validi trovati: {errori[:10]}{'...' if len(errori) > 10 else ''}")
        return False
    
    logging.info("Tabella mdl_context valida.")
    return True



# VALIDAZIONE TABELLA ROLE ASSIGNMENTS

def verifica_role_assignments(df_role_assignments, df_context, df_user) -> bool:
    """
    Verifica la coerenza della tabella mdl_role_assignments:
    - ID primari validi
    - contextid esistente in mdl_context
    - userid esistente in mdl_user
    - roleid valido (solo 3)
    """
    if not verifica_chiavi_primarie(df_role_assignments):
        logging.error("Chiavi primarie non valide in mdl_role_assignments")
        return False
    
    context_ids = set(df_context["id"].dropna().unique())
    invalid_contexts = df_role_assignments.loc[
        df_role_assignments["contextid"].apply(lambda x: x not in context_ids),
        "contextid"
    ].unique()
    if len(invalid_contexts) > 0:
        logging.error(f"contextid non validi: {invalid_contexts[:10]}{'...' if len(invalid_contexts) > 10 else ''}")
        return False
    
    user_ids = set(df_user["id"].dropna().unique())
    invalid_users = df_role_assignments.loc[
        df_role_assignments["userid"].apply(lambda x: x not in user_ids),
        "userid"
    ].unique()
    if len(invalid_users) > 0:
        logging.error(f"userid non validi: {invalid_users[:10]}{'...' if len(invalid_users) > 10 else ''}")
        return False
    
    roleids_validi = {3}
    roleids_presenti = set(df_role_assignments["roleid"].dropna().unique())
    if not roleids_presenti.issubset(roleids_validi):
        logging.error(f"roleid non validi trovati: {roleids_presenti - roleids_validi}")
        return False
    
    logging.info("Tabella mdl_role_assignments valida.")
    return True