import os
import json
import pandas as pd

def CreerJson(output_path):
    # charge le jeu de données depuis hugging face sous forme de dataframe.parquet
    df = pd.read_parquet("hf://datasets/HealthDataHub/PARHAF/data/train-00000-of-00001.parquet")

    # liste de dictionnaires où on extrait uniquement les deux attributs qui nous intéressent
    cr_set = [
    {
        "id": row["id"],
        "compte_rendu": row["documents"]["text"][0]
    }
    for _, row in df.iterrows()
    ]

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cr_set, f, indent=4, ensure_ascii=False)

    print(f"{len(cr_set)} entrées sauvegardées dans '{output_path}'.")
    return cr_set


# uniquement pour l'exécuter seul si on veut le tester séparement, sans venir de main6.py
if __name__ == "__main__":
    dossier_courant = os.path.dirname(os.path.abspath(__file__))
    dossier_src = os.path.dirname(dossier_courant)              
    racine = os.path.dirname(dossier_src)                       
    
    CreerJson(os.path.join(racine, "corpus_PARHAF_outil_6.json"))
