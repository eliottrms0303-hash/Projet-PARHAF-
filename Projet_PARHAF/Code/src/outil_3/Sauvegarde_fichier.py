import json
from src.outil_3.Classe import CaracteristiquesDocument

#------------------------------------------------------------------------
#------- Fonction permettant de sauvegarder les documents en .json ------
#------------------------------------------------------------------------

def sauvegarder_documents(liste_documents: list[CaracteristiquesDocument], chemin_fichier: str ):

    #------ Transformation des objets en dictionnaire ------
    data_to_save = [doc.to_dict() for doc in liste_documents]
    
    #------ Écriture -------
    with open(chemin_fichier, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)
    
    print(f"Succès : {len(liste_documents)} documents sauvegardés dans '{chemin_fichier}'.")
