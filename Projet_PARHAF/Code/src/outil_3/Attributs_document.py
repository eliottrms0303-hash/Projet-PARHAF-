from src.outil_3.Classe import CaracteristiquesDocument
from datasets import load_dataset


#--------------------------------------------------------------------------------
#-------- Fonction permettant de remplir les éléments fermés des documents ------
#--------------------------------------------------------------------------------

def attributs_document() :

    ds = load_dataset("HealthDataHub/PARHAF")
    documents_train = list(ds["train"])
    liste_documents = []

    for document in documents_train :

        docs = document.get("documents", {})
        scenario = document.get("suggested_scenario", {})
        abstract = document.get("structured_abstract", {}) or {}
        

       #------ Normalisation de l'âge ------
        age_info = scenario.get("age", {})
        
        if age_info.get("unit") == "ans" :
            document_age = float(age_info.get("value", 0)) / 100.0
        else :
            document_age = float(age_info.get("value", 0)) / 1200.0

        #------ Normalisation de length_of_stay ------
        length_info = abstract.get("length_of_stay") or {}
        
        if length_info.get("unit") == "ans" :
            document_length = float(length_info.get("value", 0)) * 365
        elif length_info.get("unit") == "mois" :
            document_length = float(length_info.get("value", 0)) * 30
        elif length_info.get("unit") == "heures" :
            document_length = float(length_info.get("value", 0)) / 24
        elif length_info.get("unit") == "jours" :
            document_length = float(length_info.get("value", 0))
        else :
            document_length = float(length_info.get("value", 0))


        #------ Préparation sécurisée des champs complexes ------
        def get_desc(data):
            # Si 'data' est un dictionnaire, on accède directement à la description
            if isinstance(data, dict):
                desc = data.get("description")
                # Si la description est une liste, on prend le premier élément
                if isinstance(desc, list) and len(desc) > 0:
                    return desc[0]
                return desc
            return None

        # 1. Extraction primaire_procedure
        proc_data = abstract.get("primary_procedure") or scenario.get("primary_procedure")
        proc_desc = get_desc(proc_data)
        
        # 2. Extraction primaire_diagnosis
        diag_data = abstract.get("primary_diagnosis") or scenario.get("primary_diagnosis")
        diag_desc = get_desc(diag_data)

        #------ Remplissage ------
        doc = CaracteristiquesDocument(

            #------ Métadonnées générales ------
            ID = document.get("id", ""),
            specialty = document.get("specialty", ""),
            pool = document.get("pool", ""),

            #------ Infos sur le scénario ------
            name = scenario.get("name", ""),
            age = document_age,
            sex = scenario.get("sex", ""),
            admission_mode = scenario.get("admission_mode", ""),
            discharge_mode = scenario.get("discharge_mode", ""),
            type_of_care = scenario.get("type_of_care", ""),

            #------ Infos sur le document ------
            Type = docs.get("type", []),
            header = docs.get("header", []),
            text = docs.get("text", []),

            #------ Infos sur l'abstract ------
            primary_procedure = [proc_desc] if proc_desc else [],
            primary_diagnosis = [diag_desc] if diag_desc else [],
            length_of_stay = document_length,
            vecteur = {}
        )
        liste_documents.append(doc)

    return liste_documents
