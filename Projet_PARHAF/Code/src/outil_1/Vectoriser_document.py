from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from src.outil_1.Classe import CaracteristiquesDocument

#---------------------------------------------------------------------------------
#------- Fonction permettant de vectoriser en un vecteur unique global ------------
#---------------------------------------------------------------------------------

def vectoriser_documents(liste_documents: list[CaracteristiquesDocument]):

    #------ Chargement du modèle d'embedding ------
    modele = SentenceTransformer("intfloat/multilingual-e5-small")
    
    #------ Préparation du texte enrichi ------
    textes_a_vectoriser = []
    
    for doc in liste_documents:
        fiche = (
            f"Le patient se nomme {doc.name or 'Inconnu'}. "
            f"Le patient est agé de {doc.age or 'N/A'}. "
            f"Le patient est de sex {doc.sex or 'N/A'}. "
            f"Le mode d'admission du patient est {doc.admission_mode or 'N/A'}. "
            f"Le mode de sortie du patient est {doc.discharge_mode or 'N/A'}. "
            f"Le type de soins donné au patient est {doc.type_of_care or 'N/A'}. "
            f"La spécialité du patient {doc.specialty or 'N/A'}. "
            f"Le groupe/pool du patient est {doc.pool or 'N/A'}. "
            f"Le diagnostic principal du patient est {(' '.join(doc.primary_diagnosis) if doc.primary_diagnosis else 'Non spécifié')}. "
            f"La procédure principal du patient est {(' '.join(doc.primary_procedure) if doc.primary_procedure else 'Aucune')}. "
            f"La durée du séjour du patient est {doc.length_of_stay or 'N/A'}. "
            f"Type : {(' '.join(doc.Type) if doc.Type else '')}. "
            f"Header : {(' '.join(doc.header) if doc.header else '')}. "
            f"Compte-rendu médical : {(' '.join(doc.text) if doc.text else 'Aucun contenu')}"
        )
        textes_a_vectoriser.append(fiche)
    
    #------ Embedding global ------
    print(f"Vectorisation de {len(textes_a_vectoriser)} documents en cours...")
    embeddings = modele.encode(textes_a_vectoriser, prompt="passage: ", batch_size=64, show_progress_bar=True)
    
    #------ Remplissage du vecteur unique dans chaque document ------
    for indice, document in enumerate(liste_documents):
        document.vecteur = {"global": embeddings[indice].tolist()}
