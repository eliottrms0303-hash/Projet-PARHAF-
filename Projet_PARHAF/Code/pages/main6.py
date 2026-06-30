import json
import ollama
import streamlit as st
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.outil_6.CreerJson import CreerJson

# récupère le dossier où se trouve le script python actuel
dossier_courant = os.path.dirname(os.path.abspath(__file__)) # /pages
racine = os.path.dirname(dossier_courant) # /Code

# définit les chemins par rapport à ce dossier
path_entree = os.path.join(racine, "corpus_PARHAF_outil_6.json")
path_sortie = os.path.join(racine, "src", "outil_6", "extractions.json")

# charge les données
@st.cache_data
def charger_donnees(chemin):
    # si le json n'existe pas encore sur la machine, on le génère
    if not os.path.exists(chemin):
        st.info("Téléchargement du jeu de données depuis HuggingFace, veuillez patienter.")
        CreerJson(output_path=chemin)
    try:
        with open(chemin, "r", encoding="utf-8") as fichier: # read le fichier json
            return json.load(fichier)
    except FileNotFoundError:
        st.error(f"Fichier introuvable. Assurez-vous que 'id_cr.json' ait bien été généré.")
        return []


# Configuration de la page
st.set_page_config(page_title="Extraction structurée d'informations cliniques", layout="wide")


# affiche les logos
col1, col2, col3, col4 = st.columns([4,1,1,1])

with col1 :
    st.image("Images/logo_limics.png", width = 300, use_container_width=False)
with col3 :
    st.image("Images/Logo_of_Sorbonne_University.png", width = 150, use_container_width=False)
with col4 :
    st.image("Images/Logo_Polytech_Sorbonne.png", width = 150, use_container_width=False)
st.markdown("---")

st.write('#### Rappel du sujet')
st.subheader("SUJET 6 - Extraction structurée d'informations cliniques")
st.subheader("Objectif : transformer un texte libre en structure exploitable (type JSON).")
st.write("##### Sélectionnez un ou plusieurs patients pour extraire des infos structurées depuis leur compte-rendu.")


donnees = charger_donnees(path_entree)

if donnees:
    # crée d'une liste de tous les IDs disponibles pour la barre de recherche
    liste_ids = [str(patient["id"]) for patient in donnees]

    # barre de recherche pour faire une sélection multiple
    patients_selectionnes = st.multiselect("Choisir les identifiants patients (entre 1 et 5 max pour éviter que ce soit trop long)", options=liste_ids, default=None)

    # si on sélectionne trop de patients, avertissement car ça peut prendre du temps dépendamment de la machine sur laquelle on fait tourner le script :p
    if len(patients_selectionnes) > 5:
        st.warning(f"Vous avez sélectionné {len(patients_selectionnes)} patients. Le traitement local risque d'être un peu long.")

    # bouton pour lancer le traitement
    bouton_lancer = st.button("Lancer la structuration des données")

    # traitement lors du clic
    if bouton_lancer and patients_selectionnes:
        resultats_extraits = []

        # je veux garder que les patients sélectionnés
        donnees_a_traiter = [p for p in donnees if str(p["id"]) in patients_selectionnes]

        st.subheader("En cours...")

        # barre de progression streamlit
        barre_progression = st.progress(0)

        for idx, patient in enumerate(donnees_a_traiter):
            id_patient = patient["id"]
            compte_rendu = patient["compte_rendu"]

            # met à jour le statut dans l'interface
            st.info(f"Analyse du compte-rendu {id_patient} ({idx + 1} sur {len(donnees_a_traiter)})")

            prompt = f"""
            Tu es un expert en traitement de données médicales et en extraction d'informations cliniques.
            Analyse le compte-rendu clinique suivant et segmente-le de manière structurée et exploitable (type JSON).
            Donne uniquement le JSON.

            Instructions de remplissage du JSON :
            - metadonnees : extrait le nom du patient, son âge, sa date de naissance, son sexe ("M" si : "Monsieur", "homme" / "F" si : "Madame", "femme") le médecin prescripteur ou signataire (peut être situé à la fin du texte, après 'Fait par'), quand il a été reçu, la date est située après 'Reçu le'.
            - renseignements_cliniques : extrait textuellement ce qui suit le paragraphe 'Renseignements cliniques :'.
            - antecedants : extrait les antécédants, l'histoire du patient, son mode de vie, un contexte. UNIQUEMENT si le terme antécédants, mettre les détails dans la description du type "antecedents".
            - evolutions : extrait les évolutions du patient au sein du service, comme des 'signes' ou des 'observations'
            - conclusion : extrait le résumé diagnostique final situé après 'CONCLUSION :'
            - codification : extrais le code ADICAP situé à la toute fin du compte-rendu, juste après 'Codification'.

            Si une catégorie est introuvable, mets null.

            Format JSON à respecter :
            {{
                "nom": "le nom et le prénom du patient",
                "age": l'âge du patient (nombre entier ou null si inconnu),
                "date_de_naissance": "la date de naissance du patient",
                "sexe": "M ou F (ou null si inconnu)",
                "reçu le": "la date où le patient a été reçu",
                "prescripteur": "le médecin prescripteur",
                "diagnostics": ["liste des pathologies, diagnostics identifiés"],
                "evolutions": [liste des évolutions potentielles du patient],
                "traitements": [liste traitements ou soins mentionnés],
                "antecedents": ["liste des antécédents médicaux du patient"]
                "Code ADICAP": la codification ADICAP
            }}

            Compte-rendu :
            {compte_rendu}
            """

            try:
                # appel ollama
                reponse = ollama.generate(model="llama3.2", prompt=prompt, format="json")
                texte_brut_llm = reponse["response"]

                # convertit en dico python
                donnees_json = json.loads(texte_brut_llm)
                donnees_json["id"] = id_patient
                resultats_extraits.append(donnees_json)

                # affiche les résultats en direct
                with st.expander(f"Infos structurées du compte-rendu patient correspondant à : {id_patient}", expanded=True,):
                    st.json(donnees_json)

            except Exception as e:
                st.error(f"Erreur lors du traitement du document {id_patient} : {e}")

            # met à jour la barre de progression
            barre_progression.progress((idx + 1) / len(donnees_a_traiter))

        # sauvegarde si réussite
        if resultats_extraits:
            st.success("Extraction terminée avec succès !")

            os.makedirs(os.path.dirname(path_sortie), exist_ok=True)
            
            with open(path_sortie, "w", encoding="utf-8") as f_out:
                json.dump(resultats_extraits, f_out, indent=4, ensure_ascii=False)

        st.write(f"Fichier enregistré sous : `{path_sortie}`")

elif bouton_lancer and not patients_selectionnes:
        st.sidebar.error("Veuillez sélectionner au moins un patient.")
else:
    st.info("En attente de la sélection des patients.")
