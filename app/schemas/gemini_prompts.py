"""
Prompt template per la generazione di colonne con Gemini.
I placeholder {colonna} verranno sostituiti con i valori del DataFrame.
"""



# mdl_course

prompt_fullname_course = (
    "Genera un nome di corso coerente con la seguente categoria:\n"
    "Nome: {category_name}\n"
    "Descrizione: {category_description}"
)

prompt_shortname_course = (
    "Genera un nome abbreviato per il corso '{fullname}'"
)

prompt_summary_course = (
    "Scrivi una breve descrizione del contenuto del corso intitolato '{fullname}'. "
    "La descrizione deve essere chiara, coerente con il titolo, e utile per capire gli argomenti trattati."
)

prompt_course_level = (
    "In base al contenuto del corso descritto qui sotto, assegna un livello di difficoltà da 1 a 5.\n"
    "1 = molto facile, 5 = molto difficile. \n"
    "Titolo del corso: {fullname}\n"
    "Descrizione del corso: {summary}\n"
    "Rispondi solo con il numero."
)



# mdl_resource

prompt_name_resource = (
    "Immagina una risorsa didattica testuale che rappresenti un possibile capitolo o sezione del corso descritto qui sotto.\n"
    "La risorsa può riguardare qualsiasi parte del corso, non necessariamente l'inizio.\n"
    "Nome del corso: {course_name}\n"
    "Descrizione del corso: {course_summary}\n"
    "Genera un titolo coerente e specifico per questa risorsa.\n"
    "Rispondi solo con il nome della risorsa, senza spiegazioni."
)

prompt_intro_resource = (
    "Scrivi una breve descrizione del contenuto della risorsa intitolata '{name}'. "
    "La descrizione deve essere chiara, coerente con il titolo, e utile per capire gli argomenti trattati."
)

prompt_resource_level = (
    "In base al contenuto della risorsa descritta qui sotto e al livello del corso da cui proviene, "
    "assegna un livello di difficoltà da 1 a 5.\n"
    "1 = molto facile, 5 = molto difficile.\n"
    "Livello del corso: {course_level}"
    "Titolo della risorsa: {name}\n"
    "Descrizione della risorsa: {intro}\n"
    "Rispondi solo con il numero."
)