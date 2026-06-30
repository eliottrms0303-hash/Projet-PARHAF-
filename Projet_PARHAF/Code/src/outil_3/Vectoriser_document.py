from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from src.outil_3.Classe import CaracteristiquesDocument

#---------------------------------------------------------------------------------
#------- Fonction permettant de vectoriser les éléments : nom, header, text ------
#---------------------------------------------------------------------------------

def vectoriser_documents(liste_documents : list[CaracteristiquesDocument]) :

    #------ Chargement du modèle d'embedding ~ "intfloat/multilingual-e5-small"
    modele = SentenceTransformer("intfloat/multilingual-e5-small")
    

    #------ Création de liste pour stocker les ensembles non fermés ------
    liste_nom = []
    liste_type_of_care = []
    liste_header = []
    liste_text = []
    liste_primary_procedure = []
    liste_primary_diagnosis = []
    

    #------ Stockage des attributs dans les listes ------
    for document in liste_documents :
        liste_nom.append(str(document.name) if document.name is not None else "")
        liste_type_of_care.append(str(document.type_of_care) if document.type_of_care is not None else "")
        liste_header.append(" ".join([str(h) for h in document.header]) if document.header else "")
        liste_text.append(" ".join([str(t) for t in document.text]) if document.text else "")
        liste_primary_procedure.append(" ".join([str(item) for item in document.primary_procedure]) if isinstance(document.primary_procedure, list) else str(document.primary_procedure or ""))
        liste_primary_diagnosis.append(" ".join([str(item) for item in document.primary_diagnosis]) if isinstance(document.primary_diagnosis, list) else str(document.primary_diagnosis or ""))

    #------  Embedding ------
    embedding_name = modele.encode(liste_nom, prompt="passage: ", batch_size = 64, show_progress_bar = True)
    embedding_type_of_care = modele.encode(liste_type_of_care, prompt="passage: ", batch_size = 64, show_progress_bar = True)
    embedding_header = modele.encode(liste_header, prompt="passage: ", batch_size = 64, show_progress_bar = True)
    embedding_text = modele.encode(liste_text, prompt="passage: ", batch_size = 64, show_progress_bar = True)
    embedding_primary_procedure = modele.encode(liste_primary_procedure, prompt="passage: ", batch_size = 64, show_progress_bar = True)
    embedding_primary_diagnosis = modele.encode(liste_primary_diagnosis, prompt="passage: ", batch_size = 64, show_progress_bar = True)

    #------ Remplissage des vecteurs ------
    indice = 0
    for document in liste_documents :
        document.vecteur["name"] = embedding_name[indice].tolist()
        document.vecteur["type_of_care"] = embedding_type_of_care[indice].tolist()
        document.vecteur["header"] = embedding_header[indice].tolist()
        document.vecteur["text"] = embedding_text[indice].tolist()
        document.vecteur["primary_procedure"] = embedding_primary_procedure[indice].tolist()
        document.vecteur["primary_diagnosis"] = embedding_primary_diagnosis[indice].tolist()
        indice = indice + 1

    
