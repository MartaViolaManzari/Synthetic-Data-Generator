import logging
import pandas as pd
import os
import warnings
from fastapi import Request

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

from app.services.generators.key_generator import (
    genera_chiavi_primarie,
    genera_chiavi_esterne
)
from app.services.generators.faker_generator import riempi_colonne_da_schema, riempi_utenti_coerenti
from app.schemas.faker_schemas import (
    faker_schema_user,
    faker_schema_course,
    faker_schema_resource,
    faker_schema_context,
    faker_schema_role_assignments
)
from app.services.generators.gemini_client import init_vertex_ai
from app.services.builders.gemini_builders import (
    build_course_fullname,
    build_course_shortname,
    build_course_summary,
    build_course_level,
    build_resource_name,
    build_resource_intro,
    build_resource_level
)
from app.services.builders.tag_builders import (
    genera_tabella_tag,
    genera_tabella_category_tag,
    genera_tabella_course_tag,
    genera_tabella_resource_tag
)
from app.services.builders.mdl_builders import (
    build_mdl_context,
    build_mdl_role_assignments
)
from app.services.validators.schema_validators import (
    verifica_chiavi_primarie,
    verifica_chiavi_esterne,
    verifica_context,
    verifica_role_assignments,
    verifica_unicita,
    verifica_range
)

logger = logging.getLogger(__name__)

# --- Eccezione custom ---
class ValidationError(Exception):
    pass

def check_or_raise(condition: bool, message: str):
    """Wrapper per sollevare errore se la validazione fallisce."""
    if not condition:
        raise ValidationError(message)



def safe_init_gemini():
    try:
        service_account_path = os.path.join("app", "credentials", "vertex_service_account.json")
        project_id = "prj-mlai-quelixolivet-demo-001"
        location = "us-central1"

        init_vertex_ai(project_id, location, service_account_path)
        return True
    except Exception as e:
        logger.error(f"Gemini non inizializzato: {e}")
        return False
    


# --- Orchestratore ---
def genera_dataset(n_utenti: int, n_corsi: int, n_risorse: int, json_tag_path: str):
    """
    Orchestratore end-to-end:
    1. prepara i dataset con intestazioni corrette e tabelle statiche
    2. popola con chiavi primarie e chiavi esterne
    3. genera mdl_context e mdl_role_assignments
    4. Faker per colonne non essenziali
    5. Gemini per colonne semantiche
    6. genera tabelle dei tag
    """

    logger.info("=== Avvio generazione dataset sintetico ===")

    # 1. Preparazione dataset vuoti con intestazioni
    df_user = pd.DataFrame(columns=[
        "id","auth","confirmed","policyagreed","deleted","suspended","mnethostid",
        "username","password","idnumber","firstname","lastname","email","emailstop",
        "icq","skype","yahoo","aim","msn","phone1","phone2","institution","department",
        "address","city","country","lang","calendartype","theme","timezone","firstaccess",
        "lastaccess","lastlogin","currentlogin","lastip","secret","picture","url",
        "description","descriptionformat","mailformat","maildigest","maildisplay",
        "autosubscribe","trackforums","timecreated","timemodified","trustbitmask",
        "imagealt","lastnamephonetic","firstnamephonetic","middlename","alternatename",
        "moodlenetprofile"
    ])

    df_course = pd.DataFrame(columns=[
        "id","category","sortorder","fullname","shortname","idnumber","summary","summaryformat",
        "format","showgrades","newsitems","startdate","enddate","relativedatesmode","marker",
        "maxbytes","legacyfiles","showreports","visible","visibleold","downloadcontent",
        "groupmode","groupmodeforce","defaultgroupingid","lang","calendartype","theme",
        "timecreated","timemodified","requested","enablecompletion","completionnotify",
        "cacherev","originalcourseid","showactivitydates","showcompletionconditions",
        "pdfexportfont","course_level"
    ])

    df_resource = pd.DataFrame(columns=[
        "id","course","name","intro","introformat","tobemigrated","legacyfiles",
        "legacyfileslast","display","displayoptions","filterfiles","revision",
        "timemodified","resource_level","feedback_score","uploaded_by"
    ])

    df_context = pd.DataFrame(columns=[
        "id","contextlevel","instanceid","path","depth","locked"
    ])

    df_role_assignments = pd.DataFrame(columns=[
        "id","roleid","contextid","userid","timemodified","modifierid","component","itemid","sortorder"
    ])

    # tabelle fisse
    df_course_categories = pd.DataFrame([
        [30,"Abilità Comunicative",None,"Sviluppo delle capacità di espressione, ascolto e interazione efficace.",0,0,0,0,1,1,0,0,None,None],
        [31,"Abilità Informatiche",None,"Competenze digitali e tecniche per l'uso consapevole delle tecnologie",0,0,0,0,1,1,0,0,None,None],
        [32,"Competenze in Economia",None,"Conoscenze di base e avanzate in economia, finanza e gestione.",0,0,0,0,1,1,0,0,None,None],
        [33,"Sviluppo Personale",None,"Percorsi per la crescita individuale, la motivazione e la consapevolezza.",0,0,0,0,1,1,0,0,None,None],
        [34,"Visione Imprenditoriale",None,"Formazione orientata all'innovazione, leadership e creazione d'impresa.",0,0,0,0,1,1,0,0,None,None]
    ], columns=[
        "id","name","idnumber","description","descriptionformat","parent","sortorder",
        "coursecount","visible","visibleold","timemodified","depth","path","theme"
    ])

    df_role = pd.DataFrame([
        [1,"","manager","",1,"manager"],
        [2,"","coursecreator","",2,"coursecreator"],
        [3,"","editingteacher","",3,"editingteacher"],
        [4,"","teacher","",4,"teacher"],
        [5,"","student","",5,"student"],
        [6,"","guest","",6,"guest"],
        [7,"","user","",7,"user"],
        [8,"","frontpage","",8,"frontpage"]
    ], columns=["id","name","shortname","description","sortorder","archetype"])


    # 2. Chiavi primarie e chiavi esterne
    df_user = genera_chiavi_primarie(df_user, n_utenti)
    df_course = genera_chiavi_primarie(df_course, n_corsi)
    df_resource = genera_chiavi_primarie(df_resource, n_risorse)

    check_or_raise(verifica_chiavi_primarie(df_user), "PK non valide in mdl_user")
    check_or_raise(verifica_chiavi_primarie(df_course), "PK non valide in mdl_course")
    check_or_raise(verifica_chiavi_primarie(df_resource), "PK non valide in mdl_resource")


    df_course = genera_chiavi_esterne(df_course, "category", df_course_categories, "id")
    df_resource = genera_chiavi_esterne(df_resource, "course", df_course, "id")
    df_resource = genera_chiavi_esterne(df_resource, "uploaded_by", df_user, "id")

    check_or_raise(verifica_chiavi_esterne(df_course, "category", df_course_categories, "id"),
                   "FK category non valida in mdl_course")
    check_or_raise(verifica_chiavi_esterne(df_resource, "course", df_course, "id"),
                   "FK course non valida in mdl_resource")
    check_or_raise(verifica_chiavi_esterne(df_resource, "uploaded_by", df_user, "id"),
                   "FK uploaded_by non valida in mdl_resource")
    

    # 3. context e role_assignments
    df_context = build_mdl_context(df_course, df_resource)
    df_role_assignments = build_mdl_role_assignments(df_context, df_resource, df_user)

    check_or_raise(verifica_context(df_context, df_course, df_resource), "mdl_context non valida.")
    check_or_raise(verifica_role_assignments(df_role_assignments, df_context, df_user), "mdl_role_assignments non valida.")


    # 4. Faker
    df_user = riempi_colonne_da_schema(df_user, faker_schema_user)
    df_course = riempi_colonne_da_schema(df_course, faker_schema_course)
    df_resource = riempi_colonne_da_schema(df_resource, faker_schema_resource)
    df_context = riempi_colonne_da_schema(df_context, faker_schema_context)
    df_role_assignments = riempi_colonne_da_schema(df_role_assignments, faker_schema_role_assignments)

    check_or_raise(verifica_range(df_resource, "feedback_score", 1.0, 5.0), "Valori fuori range in feedback_score")

    # 5. Gemini
    df_course = build_course_fullname(df_course, df_course_categories)
    df_course = build_course_shortname(df_course)
    df_course = build_course_summary(df_course)
    df_course = build_course_level(df_course)

    df_resource = build_resource_name(df_resource, df_course)
    df_resource = build_resource_intro(df_resource)
    df_resource = build_resource_level(df_resource, df_course)

    check_or_raise(verifica_range(df_course, "course_level", 1, 5), "Valori fuori range in course_level")
    check_or_raise(verifica_range(df_resource, "resource_level", 1, 5), "Valori fuori range in resource_level")


    # 6. Tag
    df_tag = genera_tabella_tag(json_tag_path)
    df_category_tag = genera_tabella_category_tag(json_tag_path, df_course_categories, df_tag)
    df_course_tag = genera_tabella_course_tag(df_course, df_category_tag, df_tag)
    df_tag, df_resource_tag = genera_tabella_resource_tag(df_resource, df_tag)

    check_or_raise(verifica_unicita(df_tag, "name"), "Duplicati in tag.name")

    logger.info("=== Dataset generato e validato con successo ===")

    return {
        "user": df_user,
        "course": df_course,
        "resource": df_resource,
        "context": df_context,
        "role": df_role,
        "role_assignments": df_role_assignments,
        "course_categories": df_course_categories,
        "tag": df_tag,
        "category_tag": df_category_tag,
        "course_tag": df_course_tag,
        "resource_tag": df_resource_tag
    }



# versione a step
def genera_dataset_steps(n_utenti: int, n_corsi: int, n_risorse: int, request: Request):
    """
    Orchestratore end-to-end:
    1. prepara i dataset con intestazioni corrette e tabelle statiche
    2. popola con chiavi primarie e chiavi esterne
    3. genera mdl_context e mdl_role_assignments
    4. Faker per colonne non essenziali
    5. Gemini per colonne semantiche
    6. genera tabelle dei tag
    """

    logger.info("=== Avvio generazione dataset sintetico ===")

    # path fisso al file JSON
    json_tag_path = os.path.join("app", "data", "tag_map.json")

    # 1. Preparazione dataset vuoti con intestazioni
    yield {"progress": 0, "message": "Preparazione dataset..."}

    df_user = pd.DataFrame(columns=[
        "id","auth","confirmed","policyagreed","deleted","suspended","mnethostid",
        "username","password","idnumber","firstname","lastname","email","emailstop",
        "icq","skype","yahoo","aim","msn","phone1","phone2","institution","department",
        "address","city","country","lang","calendartype","theme","timezone","firstaccess",
        "lastaccess","lastlogin","currentlogin","lastip","secret","picture","url",
        "description","descriptionformat","mailformat","maildigest","maildisplay",
        "autosubscribe","trackforums","timecreated","timemodified","trustbitmask",
        "imagealt","lastnamephonetic","firstnamephonetic","middlename","alternatename",
        "moodlenetprofile"
    ])

    df_course = pd.DataFrame(columns=[
        "id","category","sortorder","fullname","shortname","idnumber","summary","summaryformat",
        "format","showgrades","newsitems","startdate","enddate","relativedatesmode","marker",
        "maxbytes","legacyfiles","showreports","visible","visibleold","downloadcontent",
        "groupmode","groupmodeforce","defaultgroupingid","lang","calendartype","theme",
        "timecreated","timemodified","requested","enablecompletion","completionnotify",
        "cacherev","originalcourseid","showactivitydates","showcompletionconditions",
        "pdfexportfont","course_level"
    ])

    df_resource = pd.DataFrame(columns=[
        "id","course","name","intro","introformat","tobemigrated","legacyfiles",
        "legacyfileslast","display","displayoptions","filterfiles","revision",
        "timemodified","resource_level","feedback_score","uploaded_by"
    ])

    df_context = pd.DataFrame(columns=[
        "id","contextlevel","instanceid","path","depth","locked"
    ])

    df_role_assignments = pd.DataFrame(columns=[
        "id","roleid","contextid","userid","timemodified","modifierid","component","itemid","sortorder"
    ])

    # tabelle fisse
    df_course_categories = pd.DataFrame([
        [30,"Abilità Comunicative",None,"Sviluppo delle capacità di espressione, ascolto e interazione efficace.",0,0,0,0,1,1,0,0,None,None],
        [31,"Abilità Informatiche",None,"Competenze digitali e tecniche per l'uso consapevole delle tecnologie",0,0,0,0,1,1,0,0,None,None],
        [32,"Competenze in Economia",None,"Conoscenze di base e avanzate in economia, finanza e gestione.",0,0,0,0,1,1,0,0,None,None],
        [33,"Sviluppo Personale",None,"Percorsi per la crescita individuale, la motivazione e la consapevolezza.",0,0,0,0,1,1,0,0,None,None],
        [34,"Visione Imprenditoriale",None,"Formazione orientata all'innovazione, leadership e creazione d'impresa.",0,0,0,0,1,1,0,0,None,None]
    ], columns=[
        "id","name","idnumber","description","descriptionformat","parent","sortorder",
        "coursecount","visible","visibleold","timemodified","depth","path","theme"
    ])

    df_role = pd.DataFrame([
        [1,"","manager","",1,"manager"],
        [2,"","coursecreator","",2,"coursecreator"],
        [3,"","editingteacher","",3,"editingteacher"],
        [4,"","teacher","",4,"teacher"],
        [5,"","student","",5,"student"],
        [6,"","guest","",6,"guest"],
        [7,"","user","",7,"user"],
        [8,"","frontpage","",8,"frontpage"]
    ], columns=["id","name","shortname","description","sortorder","archetype"])


    # 2. Chiavi primarie e chiavi esterne
    yield {"progress": 15, "message": "Generazione chiavi primarie e chiavi esterne..."}

    df_user = genera_chiavi_primarie(df_user, n_utenti)
    df_course = genera_chiavi_primarie(df_course, n_corsi)
    df_resource = genera_chiavi_primarie(df_resource, n_risorse)

    check_or_raise(verifica_chiavi_primarie(df_user), "PK non valide in mdl_user")
    check_or_raise(verifica_chiavi_primarie(df_course), "PK non valide in mdl_course")
    check_or_raise(verifica_chiavi_primarie(df_resource), "PK non valide in mdl_resource")


    df_course = genera_chiavi_esterne(df_course, "category", df_course_categories, "id")
    df_resource = genera_chiavi_esterne(df_resource, "course", df_course, "id")
    df_resource = genera_chiavi_esterne(df_resource, "uploaded_by", df_user, "id")

    check_or_raise(verifica_chiavi_esterne(df_course, "category", df_course_categories, "id"),
                   "FK category non valida in mdl_course")
    check_or_raise(verifica_chiavi_esterne(df_resource, "course", df_course, "id"),
                   "FK course non valida in mdl_resource")
    check_or_raise(verifica_chiavi_esterne(df_resource, "uploaded_by", df_user, "id"),
                   "FK uploaded_by non valida in mdl_resource")
    

    # 3. context e role_assignments
    yield {"progress": 30, "message": "Popolamento mdl_context e mdl_role_assignments..."}

    df_context = build_mdl_context(df_course, df_resource)
    df_role_assignments = build_mdl_role_assignments(df_context, df_resource, df_user)

    check_or_raise(verifica_context(df_context, df_course, df_resource), "mdl_context non valida.")
    check_or_raise(verifica_role_assignments(df_role_assignments, df_context, df_user), "mdl_role_assignments non valida.")


    # 4. Faker
    yield {"progress": 45, "message": "Generazione con Faker..."}

    df_user = riempi_colonne_da_schema(df_user, faker_schema_user)
    df_user = riempi_utenti_coerenti(df_user)
    df_course = riempi_colonne_da_schema(df_course, faker_schema_course)
    df_resource = riempi_colonne_da_schema(df_resource, faker_schema_resource)
    df_context = riempi_colonne_da_schema(df_context, faker_schema_context)
    df_role_assignments = riempi_colonne_da_schema(df_role_assignments, faker_schema_role_assignments)

    check_or_raise(verifica_range(df_resource, "feedback_score", 1.0, 5.0), "Valori fuori range in feedback_score")

    # 5. Gemini
    yield {"progress": 60, "message": "Generazione con Gemini..."}

    if safe_init_gemini():
        df_course = build_course_fullname(df_course, df_course_categories)
        df_course = build_course_shortname(df_course)
        df_course = build_course_summary(df_course)
        df_course = build_course_level(df_course)

        df_resource = build_resource_name(df_resource, df_course)
        df_resource = build_resource_intro(df_resource)
        df_resource = build_resource_level(df_resource, df_course)

        check_or_raise(verifica_range(df_course, "course_level", 1, 5), "Valori fuori range in course_level")
        check_or_raise(verifica_range(df_resource, "resource_level", 1, 5), "Valori fuori range in resource_level")


    # 6. Tag
    yield {"progress": 90, "message": "Generazione tag..."}
    df_tag = genera_tabella_tag(json_tag_path)
    df_category_tag = genera_tabella_category_tag(json_tag_path, df_course_categories, df_tag)
    df_course_tag = genera_tabella_course_tag(df_course, df_category_tag, df_tag)
    df_tag, df_resource_tag = genera_tabella_resource_tag(df_resource, df_tag)

    check_or_raise(verifica_unicita(df_tag, "name"), "Duplicati in tag.name")

    logger.info("=== Dataset generato e validato con successo ===")

    df_user = df_user.fillna("").infer_objects(copy=False)
    df_course = df_course.fillna("").infer_objects(copy=False)
    df_resource = df_resource.fillna("").infer_objects(copy=False)
    df_context = df_context.fillna("").infer_objects(copy=False)
    df_role = df_role.fillna("").infer_objects(copy=False)
    df_role_assignments = df_role_assignments.fillna("").infer_objects(copy=False)
    df_course_categories = df_course_categories.fillna("").infer_objects(copy=False)
    df_tag = df_tag.fillna("").infer_objects(copy=False)
    df_category_tag = df_category_tag.fillna("").infer_objects(copy=False)
    df_course_tag = df_course_tag.fillna("").infer_objects(copy=False)
    df_resource_tag = df_resource_tag.fillna("").infer_objects(copy=False)

    result = {
        "mdl_user": df_user.to_dict(orient="records"),
        "mdl_course": df_course.to_dict(orient="records"),
        "mdl_resource": df_resource.to_dict(orient="records"),
        "mdl_context": df_context.to_dict(orient="records"),
        "mdl_role": df_role.to_dict(orient="records"),
        "mdl_role_assignments": df_role_assignments.to_dict(orient="records"),
        "mdl_course_categories": df_course_categories.to_dict(orient="records"),
        "tag": df_tag.to_dict(orient="records"),
        "category_tag": df_category_tag.to_dict(orient="records"),
        "course_tag": df_course_tag.to_dict(orient="records"),
        "resource_tag": df_resource_tag.to_dict(orient="records")
    }

    request.app.state.last_dfs = {
        "mdl_user": df_user,
        "mdl_course": df_course,
        "mdl_resource": df_resource,
        "mdl_context": df_context,
        "mdl_role": df_role,
        "mdl_role_assignments": df_role_assignments,
        "mdl_course_categories": df_course_categories,
        "tag": df_tag,
        "category_tag": df_category_tag,
        "course_tag": df_course_tag,
        "resource_tag": df_resource_tag
    }

    yield {
        "progress": 100, 
        "message": "Generazione dati sintetici completata!", 
        "result": result
    }
    return
    