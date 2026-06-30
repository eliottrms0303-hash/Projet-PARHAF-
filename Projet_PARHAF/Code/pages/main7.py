import streamlit as st
import os
import sys
from pathlib import Path
from datasets import load_dataset
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# On importe des fonctions depuis src/outil_7/
# (comme main1.py importe depuis src/outil_1/)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.outil_7.extraction import extraire_evenements
from src.outil_7.tri import trier_et_filtrer
from src.outil_7.frise import construire_frise

# PROMPT 

gabarit_extraction = """
Tu es un expert en extraction chronologique d'événements médicaux.

Tu dois analyser UNIQUEMENT le texte fourni dans la section :
=== TEXTE À ANALYSER ===

Tu dois produire un JSON strictement valide, sans texte autour.

RÈGLES IMPORTANTES :
1. TOUTES les informations doivent être extraites uniquement du texte fourni, sans aucune inférence ou ajout d'information extérieure.
2. N'utilise jamais les exemples comme contenu médical.
3. Ne mets aucune donnée personnelle : pas de nom, prénom, âge, sexe, date de naissance, adresse, médecin.
4. Ignore les dates de naissance.
5. Pour un compte rendu, extrais dans l'ordre suivant:
   - les renseignements cliniques s'ils existent ;
   - l'acte principal comme examen paraclinique ;
   - le diagnostic à partir de la section Conclusion.
6.UNIQUEMENT si le terme antécédants, mettre les détails dans la description du type "Antécédents" avec la date 0000/00/00.
7.UNIQUEMENTT si le terme contexte apparait, mettre les détails dans la description du type "Contexte".
8.UNIQUEMENT si des termes faisant référence à une "Sortie à domicile", "retour à domicile", "sortir" ou "transfert" dans le **Texte**, ils doivent être dans la description du type "Sortie".
9. ATTENTION: Les événements doivent être listés dans l'ordre où ils apparaissent dans le compte rendu.
10. IMPORTANT : Les examens comme scanner, IRM, échographie, **Radiographie**, **Artériographie cérébrale**,ECG, tériographie, bilan biologique, **BIOPSIES**, doivent être sous "Examens paracliniques", IGNORE les autres examens.
11. Ne détaille pas MACROSCOPIE et MICROSCOPIE, détails des examans cliniques inutiles.
12. Ne mets pas les noms propres : écris seulement "Le patient" ou "La patiente".
13. Si une section Conclusion existe, elle doit produire un événement de type Diagnostic.
14.Ne crée jamais d'événement Hospitalisation sauf si le mot "hospitalisation" est écrit explicitement dans le texte.
15.Uniquement si le terme **traitements d'entrée**  SI PRESENTS doit être sous "Traitements entree".
16. Uniquement si le terme **traitements de sortie**  SI PRESENTS doit être sous "Traitements sortie", GENERALEMENT présents autour de la Conclusion.
17. chaque type possède IMPERATIVEMENT une date au format AAAA/MM/JJ.

ATTENTION: A PRENDRE EN COMPTE IMPERATIVEMENT:
- ne crée jamais d'événement Hospitalisation sauf si le mot "hospitalisation" est écrit explicitement dans le texte ;
- l'événement Examens paracliniques doit correspondre à l'acte principal du compte rendu, souvent écrit en majuscules, par exemple : biopsies bronchiques, micro-biopsies, biopsie du sein, pièce opératoire ;
- ne remplace pas cet acte principal par les détails de microscopie ou d'immunohistochimie ;
- Si scanner, IRM, échographie, **Radiographie**, **Artériographie cérébrale**,ECG, tériographie, bilan biologique, **Biopsies**, à METTRE être sous "Examens paracliniques", surtout quand une date sous la forme AAAA/MM/JJ est associée.
- IMPORTANT: Dès que des termes faisant référence à une **Sortie à domicile**, **retour à domicile**, **sortir** ou **transfert**, ils doivent être dans la description du type "Sortie".

REGLE A PRENDRE EN COMPTE IMPERATIVEMENT SUR LES DATES:
- CHAQUE TYPE doit impérativement avoir une date valide, sous la forme AAAA/MM/JJ.
- Si une période est écrite "du JJ/MM/AAAA au JJ/MM/AAAA", utilise UNIQUEMENT la date de début (JJ/MM/AAAA) pour l'événement.
- Si le document possède une UNIQUE date, utilise cette date pour tous les types du document de sorte à ce que CHAQUE évènement ait une date valide.
- Si un événement n'a pas de date propre, utilise la date de l'évènement précédent ou prochain.
- IGNORE les dates de naissance, même si elles sont écrites dans le texte.
- Si la date d'un examen est floue ("récemment", "il y a 3 mois", "2 jours plus tard", etc.), 
  calcule une date approximative à partir de la date de référence du document et utilise-la au format AAAA/MM/JJ.
- dès que un type **Antécédents** est créé, il doit impérativement avoir la date 0000/00/00 (pour ne pas fausser la chronologie de la timeline)

RÈGLE SUR LES EXAMENS PARACLINIQUES ET LES DATES :
- Si plusieurs examens paracliniques ont des dates DIFFÉRENTES, crée un événement séparé pour chacun.
- Ne regroupe jamais deux examens de dates différentes dans le même événement.
- Chaque événement Examens paracliniques ne doit contenir qu'une seule date.

TYPES AUTORISÉS UNIQUEMENT ET INDEX DE PRIORITÉ :
- Contexte = 0
- Antécédents = 0
- Hospitalisation = 1
- Consultation = 1
- Renseignements cliniques = 1
- Traitements entree = 2
- Examens paracliniques = 3
- Traitements sortie = 4
- Diagnostic = 5
- Sortie = 6



STRUCTURE JSON OBLIGATOIRE :
{{
  "evenements": [
    {{
      "type": "Type de l'événement",
      "description": "Description concise extraite du texte",
      "date": "AAAA/MM/JJ",
      "index_priorite": 0
    }}
  ]
}}

=== TEXTE À ANALYSER ===

Type de document : {type_document}

Compte rendu clinique :
{texte_medical}

=== FIN DU TEXTE À ANALYSER ===

Génère uniquement le JSON valide.
Réponds UNIQUEMENT avec le JSON brut, sans balises markdown, sans ```json, sans texte avant ni après.
"""
#remarque: #double {{}} car LongChain utilise les simples {} pour repérer ses variables --> d'où double {} pour dire que c format json et que Longchain doit pas y toucher 

def main():

    # Configuration de la page
    st.set_page_config(page_title="Timeline médicale", layout="wide")

    # Logos haut de page
    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
    with col1:
        st.image("Images/logo_limics.png", width=300)
    with col3:
        st.image("Images/Logo_of_Sorbonne_University.png", width=150)
    with col4:
        st.image("Images/Logo_Polytech_Sorbonne.png", width=150)

    # Trait horizontal 
    st.markdown("---")

    # Titre et explications
    st.subheader("🗓️ Timeline médicale d'un patient")
    st.markdown("**Objectif** : Reconstruire la chronologie des événements médicaux clés d'un patient à partir de ses comptes rendus cliniques.")
    st.markdown("**Données** : Corpus PARHAF — comptes rendus médicaux fictifs en français.")
    st.markdown("**Fonctionnement** : Un LLM extrait les événements clés de chaque compte rendu, qui sont ensuite triés chronologiquement d'une manière logique visualisés sous forme de frise.")
    st.markdown("---")

    # Chargement du corpus (une seule fois grâce au cache) 
    # @st.cache_resource évite de recharger le corpus à chaque interaction
    @st.cache_resource
    def charger_corpus():
        df = load_dataset("HealthDataHub/PARHAF")
        nom_partition = list(df.keys())[0]
        return df[nom_partition]

    #Chargement du LLM (une seule fois) 
    @st.cache_resource
    def charger_llm():
        # configuration du LLM avec ChatOllama, modèle mistral-nemo, température 0 pour plus de précision, format JSON
        generateur = ChatOllama(model="llama3.2", temperature=0, format="json") #choix de mistral-nemo car plus précis pour les textes médicaux que llama3.2; 
       
        # à remplacer par la clé open AI qui va nous être fourni (enlevez l'option commentaire des lignes suivantes)
        # generateur_llm = ChatOpenAI(
                           # model="gpt-4.1-mini",
                           # api_key="sk-",   # ← coller votre clé open AI ici
                           # temperature=0)
       
        prompt = PromptTemplate.from_template(gabarit_extraction) #transforme  texte brut en un moule dynamique --> il repère automatiquement les variables de texte entre {}
        return prompt | generateur  # chaîne LangChain complète: #résultat du prompt_template en remplaçant les champs propulsé ds le cerveau du générateur

    patients_parhaf = charger_corpus()
    chaine_extraction = charger_llm()

    # Saisie de l'id patient
    st.subheader("1 - Sélection du patient")
    id_entree = st.text_input(
        "Entrez l'identifiant du patient (ex: CARDIOLOGIE-00084)"
    ).strip().upper()

    # Bouton de lancement
    if st.button("Générer la timeline"):

        if not id_entree:
            # st.warning affiche un message orange d'avertissement
            st.warning("Veuillez entrer un identifiant patient.")
        else:
            # Extraction 
            # st.spinner affiche un message de chargement pendant le traitement
            with st.spinner("Extraction des événements en cours... (peut prendre quelques minutes)"):
                evenements = extraire_evenements(id_entree, patients_parhaf, chaine_extraction)

            if not evenements:
                # st.error affiche un message rouge d'erreur
                st.error(f"Aucun patient trouvé avec l'identifiant : {id_entree}")
            else:
                # Tri chronologique
                with st.spinner("Tri chronologique..."):
                    timeline = trier_et_filtrer(evenements)

                # st.success affiche un message vert de succès
                st.success(f"{len(timeline)} événements extraits et triés.")

                # Affichage de la frise
                st.subheader("2 - Timeline chronologique")
                fig = construire_frise(timeline, id_entree)
                st.plotly_chart(fig, use_container_width=True) #pr tracer ; # use_container_width=True → la frise prend toute la largeur.

                # Détail des événements 
                # st.expander crée un bloc repliable
                with st.expander("Voir le détail des événements"):
                    for ev in timeline:
                        st.markdown(
                            f"**[{ev.get('date')}] {ev.get('type')}** — {ev.get('description', '')}"
                        )

if __name__ == "__main__":
    main()
