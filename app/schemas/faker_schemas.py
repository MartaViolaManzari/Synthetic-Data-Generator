"""
Schemi di configurazione per la generazione di dati sintetici con Faker.
Ogni schema è un dizionario: {colonna: {"func": nome_funzione, "args": {...}}}
Le funzioni corrispondono a quelle definite in app/services/generators/faker_generator.py
"""

# schema per mdl_context
faker_schema_context = {
    "path": {"func": "riempi_colonna_null"},
    "depth": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "locked": {"func": "riempi_colonna_default", "args": {"valore": 0}}
}

# schema per mdl_course
faker_schema_course = {
    "sortorder": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "idnumber": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "summaryformat": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "format": {"func": "riempi_colonna_lista", "args": {"valori": ["topics", "weeks", "site"]}},
    "showgrades": {"func": "riempi_colonna_default", "args": {"valore": 1}},
    "newsitems": {"func": "riempi_colonna_default", "args": {"valore": 1}},
    "startdate": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "enddate": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "relativedatesmode": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "marker": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "maxbytes": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "legacyfiles": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "showreports": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "visible": {"func": "riempi_colonna_default", "args": {"valore": 1}},
    "visibleold": {"func": "riempi_colonna_default", "args": {"valore": 1}},
    "downloadcontent": {"func": "riempi_colonna_null"},
    "groupmode": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "groupmodeforce": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "defaultgroupingid": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "lang": {"func": "riempi_colonna_default", "args": {"valore": "it"}},
    "calendartype": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "theme": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "timecreated": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "timemodified": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "requested": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "enablecompletion": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "completionnotify": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "cacherev": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "originalcourseid": {"func": "riempi_colonna_null"},
    "showactivitydates": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "showcompletionconditions": {"func": "riempi_colonna_default", "args": {"valore": 1}},
    "pdfexportfont": {"func": "riempi_colonna_null"}
}

# schema per mdl_resource
faker_schema_resource = {
    "introformat": {"func": "riempi_colonna_default", "args": {"valore": 1}},
    "tobemigrated": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "legacyfiles": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "legacyfileslast": {"func": "riempi_colonna_null"},
    "display": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "displayoptions": {"func": "riempi_colonna_null"},
    "filterfiles": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "revision": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "timemodified": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "feedback_score": {"func": "riempi_colonna_float_range", "args": {"minimo": 1.0, "massimo": 5.0, "decimali": 1}}
}

# schema per mdl_role_assignments
faker_schema_role_assignments = {
    "timemodified": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "modifierid": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "component": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "itemid": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "sortorder": {"func": "riempi_colonna_default", "args": {"valore": 0}}
}

# schema per mdl_user
faker_schema_user = {
    "auth": {"func": "riempi_colonna_lista", "args": {"valori": ["email", "manual", "oauth2"]}},
    "confirmed": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "policyagreed": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "deleted": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "suspended": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "mnethostid": {"func": "riempi_colonna_default", "args": {"valore": 1}},
    "password": {"func": "riempi_colonna_faker", "args": {"tipo": "password"}},
    "idnumber": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "emailstop": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "icq": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "skype": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "yahoo": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "aim": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "msn": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "phone1": {"func": "riempi_colonna_faker", "args": {"tipo": "telefono"}},
    "phone2": {"func": "riempi_colonna_faker", "args": {"tipo": "telefono"}},
    "institution": {"func": "riempi_colonna_faker", "args": {"tipo": "istituzione"}},
    "department": {"func": "riempi_colonna_faker", "args": {"tipo": "dipartimento"}},
    "address": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "city": {"func": "riempi_colonna_faker", "args": {"tipo": "città"}},
    "country": {"func": "riempi_colonna_default", "args": {"valore": "IT"}},
    "lang": {"func": "riempi_colonna_default", "args": {"valore": "it"}},
    "calendartype": {"func": "riempi_colonna_default", "args": {"valore": "gregorian"}},
    "theme": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "timezone": {"func": "riempi_colonna_default", "args": {"valore": 99}},
    "firstaccess": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "lastaccess": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "lastlogin": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "currentlogin": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "lastip": {"func": "riempi_colonna_faker", "args": {"tipo": "ip"}},
    "secret": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "picture": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "url": {"func": "riempi_colonna_default", "args": {"valore": ""}},
    "description": {"func": "riempi_colonna_null"},
    "descriptionformat": {"func": "riempi_colonna_default", "args": {"valore": 1}},
    "mailformat": {"func": "riempi_colonna_default", "args": {"valore": 1}},
    "maildigest": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "maildisplay": {"func": "riempi_colonna_default", "args": {"valore": 2}},
    "autosubscribe": {"func": "riempi_colonna_default", "args": {"valore": 1}},
    "trackforums": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "timecreated": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "timemodified": {"func": "riempi_colonna_faker", "args": {"tipo": "timestamp"}},
    "trustbitmask": {"func": "riempi_colonna_default", "args": {"valore": 0}},
    "imagealt": {"func": "riempi_colonna_null"},
    "lastnamephonetic": {"func": "riempi_colonna_null"},
    "firstnamephonetic": {"func": "riempi_colonna_null"},
    "middlename": {"func": "riempi_colonna_null"},
    "alternatename": {"func": "riempi_colonna_null"},
    "moodlenetprofile": {"func": "riempi_colonna_null"}
}