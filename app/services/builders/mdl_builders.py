import pandas as pd
import logging

logger = logging.getLogger(__name__)

def build_mdl_context(df_course: pd.DataFrame, df_resource: pd.DataFrame) -> pd.DataFrame:
    """
    Costruisce la tabella mdl_context a partire da corsi e risorse.
    """
    context_rows = []
    context_id_counter = 1

    # corsi -> contextlevel 50
    for _, course in df_course.iterrows():
        context_rows.append({
            'id': context_id_counter,
            'contextlevel': 50,
            'instanceid': int(course['id']),
            'path': '',
            'depth': '',
            'locked': ''
        })
        context_id_counter += 1

    # risorse -> contextlevel 70
    for _, resource in df_resource.iterrows():
        context_rows.append({
            'id': context_id_counter,
            'contextlevel': 70,
            'instanceid': int(resource['id']),
            'path': '',
            'depth': '',
            'locked': ''
        })
        context_id_counter += 1

    df_context = pd.DataFrame(context_rows)        
    return df_context


def build_mdl_role_assignments(df_context: pd.DataFrame, df_resource: pd.DataFrame, df_user: pd.DataFrame) -> pd.DataFrame:
    """
    Costruisce la tabella mdl_role_assignments a partire da context, risorse e utenti.
    """
    role_assignments_rows = []
    role_assignments_id_counter = 1

    for _, context in df_context.iterrows():
        context_id = context['id']
        contextlevel = context['contextlevel']
        instance_id = context['instanceid']

        if contextlevel == 50:
            userid = df_user.sample(1).iloc[0]['id']

        elif contextlevel == 70:
            resource_match = df_resource[df_resource['id'] == instance_id]
            if not resource_match.empty and 'uploaded_by' in resource_match.columns:
                userid = resource_match.iloc[0]['uploaded_by']
            else:
                userid = df_user.sample(1).iloc[0]['id']
        else:
            continue
        
        role_assignments_rows.append({
            'id': int(role_assignments_id_counter),
            'roleid': 3,
            'contextid': int(context_id),
            'userid': int(userid),
            'timemodified': '',
            'modifierid': '',
            'component': '',
            'itemid': '',
            'sortorder': ''
        })
        role_assignments_id_counter += 1
    
    df_role_assignments = pd.DataFrame(role_assignments_rows)
    return df_role_assignments