import vertexai
from google.auth import exceptions as google_auth_exceptions
from google.oauth2 import service_account
import logging

def init_vertex_ai(project_id: str, location: str, service_account_path: str):
    try:
        credentials = service_account.Credentials.from_service_account_file(service_account_path)
        vertexai.init(project=project_id, location=location, credentials=credentials)
        logging.info("Vertex AI inizializzato correttamente")
    except google_auth_exceptions.GoogleAuthError as e:
        logging.error(f"Errore di autenticazione: {e}")
        raise