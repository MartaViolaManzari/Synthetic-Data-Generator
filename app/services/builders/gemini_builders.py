import pandas as pd
import logging
from app.services.generators.gemini_generator import riempi_colonna_gemini
from app.services.utils.helpers import get_value_by_id, valida_interi
from app.schemas import gemini_prompts as prompts

logger = logging.getLogger(__name__)



# mdl_course

def build_course_fullname(df_course: pd.DataFrame, df_course_categories: pd.DataFrame) -> pd.DataFrame:
    colonne_temp = {
    "category_name": lambda row: get_value_by_id(df_course_categories, row["category"], "name"),
    "category_description": lambda row: get_value_by_id(df_course_categories, row["category"], "description")
    }
    return riempi_colonna_gemini(
        df_course,
        "fullname",
        prompts.prompt_fullname_course,
        colonne_temp=colonne_temp,
        batch_size=500
    )

def build_course_shortname(df_course: pd.DataFrame) -> pd.DataFrame:
    return riempi_colonna_gemini(
        df_course,
        "shortname",
        prompts.prompt_shortname_course
    )

def build_course_summary(df_course: pd.DataFrame) -> pd.DataFrame:
    return riempi_colonna_gemini(
        df_course,
        "summary",
        prompts.prompt_summary_course,
        batch_size=20
    )

def build_course_level(df_course: pd.DataFrame) -> pd.DataFrame:
    return riempi_colonna_gemini(
        df_course,
        "course_level",
        prompts.prompt_course_level,
        validatore=valida_interi
    )



# mdl_resource

def build_resource_name(df_resource: pd.DataFrame, df_course: pd.DataFrame) -> pd.DataFrame:
    colonne_temp = {
        "course_name": lambda row: get_value_by_id(df_course, row["course"], "fullname"),
        "course_summary": lambda row: get_value_by_id(df_course, row["course"], "summary")
    }
    return riempi_colonna_gemini(
        df_resource,
        "name",
        prompts.prompt_name_resource,
        colonne_temp=colonne_temp,
        batch_size=25
    )

def build_resource_intro(df_resource: pd.DataFrame) -> pd.DataFrame:
    return riempi_colonna_gemini(
        df_resource,
        "intro",
        prompts.prompt_intro_resource,
        batch_size=25
    )

def build_resource_level(df_resource: pd.DataFrame, df_course: pd.DataFrame) -> pd.DataFrame:
    colonne_temp = {
        "course_level": lambda row: get_value_by_id(df_course, row["course"], "course_level")
    }
    return riempi_colonna_gemini(
        df_resource,
        "resource_level",
        prompts.prompt_resource_level,
        colonne_temp=colonne_temp,
        batch_size=100,
        validatore=valida_interi
    )