import streamlit as st
import os
import json
import sys
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
from sentence_transformers import SentenceTransformer

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.outil_1.Attributs_document import attributs_document
from src.outil_1.Classe import CaracteristiquesDocument
from src.outil_1.Vectoriser_document import vectoriser_documents
from src.outil_1.Sauvegarde_fichier import sauvegarder_documents

racine = Path(__file__).resolve().parent.parent
chemin_json = racine / "corpus_PARHAF_outil_1.json"

@st.cache_resource
def charger_modele_embedding():
    print("Chargement du modèle d'embedding en mémoire...")
    return SentenceTransformer("intfloat/multilingual-e5-small")

# APRÈS (nouvelle version)
def rechercher_candidats(question, base_de_donnees, modele):
    question_lower = question.lower()
    vecteur_question = modele.encode(f"query: {question}")
    
    scores = []
    for doc in base_de_donnees:
        score_vecteur = cosine_similarity(
            [vecteur_question], 
            [np.array(doc['vecteur']['global'])]
        )[0][0]
        
        nom = doc.get("name", "").lower()
        bonus_nom = 0.3 if nom and nom in question_lower else 0.0
        
        id_doc = doc.get("ID", "").lower()
        bonus_id = 0.5 if id_doc and id_doc in question_lower else 0.0
        
        score_final = score_vecteur + bonus_nom + bonus_id
        scores.append((score_final, doc))
    
    scores.sort(key=lambda x: x[0], reverse=True)
    return [scores[0][1]]

def main():
    st.set_page_config(page_title="Chatbot basé sur un dossier patient", layout="wide")

    # Mémoire affichage Streamlit
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Mémoire LangChain (objets HumanMessage / AIMessage)
    if "historique_llm" not in st.session_state:
        st.session_state.historique_llm = []
    # Document fixé
    if "document_courant" not in st.session_state:
        st.session_state.document_courant = None
    # Patient fixé
    if "patient_courant" not in st.session_state:
        st.session_state.patient_courant = None

    # Vérification de l'existence du json
    nom_fichier = "corpus_PARHAF_outil_1.json"

    if chemin_json.exists():
        print(f"Le fichier json {json} existe.")
    else:
        print(f"Traitement du corpus PARHAF en cours...")
        mes_documents = attributs_document()

        print(f"Vectorisation des attributs...")
        vectoriser_documents(mes_documents)

        print(f"Sauvegarde du corpus...")
        sauvegarder_documents(mes_documents, str(chemin_json))

    @st.cache_data
    def charger_base_de_donnees():
        with open(chemin_json, "r", encoding="utf-8") as f:
            return json.load(f)

    base_de_donnees = charger_base_de_donnees()

    modele = "llama3.2"
    llm = ChatOllama(model=modele, temperature=0)
    embedding = charger_modele_embedding()

    systeme_prompt = """
        Tu es un assistant médical expert en extraction et compréhension de dosiers patients.

        DONNEES DISPONIBLES :
        Pour cette session, tu disposes du dossier structuré d'UN SEUL patient.
        Les champs disponibles sont : Nom, Âge, Sexe, Spécialité, Pool, Mode d'admission,
        Mode de sortie, Type de soins, Type de document, En-tête, Compte-rendu,
        Procédure principale, Diagnostic principal, Durée de séjour.

        RÈGLES STRICTES :
        1. CONTEXTE : Tu disposes des données d'UN SEUL patient.
        2. EXHAUSTIVITÉ : Extrais TOUTES les valeurs présentes.
        3. ISOLATION : reponds UNIQUEMENT et IMPERATIVEMENT aux questions concernant le **patient identifié**. Si un patient a été identifié, continue de parler de lui uniquement, sans ambiguité.
        4. FORMATAGE TEXTUEL (CRUCIAL) :
            - Pour les champs textuels longs (Type de document, En-tête, Compte-rendu) : EVITE de RÉSUMER, affiche le contenu textuel de manière détaillée.
            - Tu DOIS restituer le contenu textuel de manière détaillée.
        5. ATTRIBUTS : Nom, Age, Sexe, Spécialité, Pool, Mode d'admission, Mode de sortie, Type de soins, Type, Titre, Procédure principale, Diagnostic principal, Durée du séjour.
        6. QUESTION SIMPLE : Si l'utilisateur demande une info précise, donne cette info et rien d'autre.
        7. Si l'information est absente, écris "Non renseigné".
        8. MÉMOIRE : Tu te souviens des échanges précédents de cette session. Si le patient a déjà été mentionné, continue à parler de lui sans jamais introduire d'ambiguïté ou de correction sur son nom. Ne cite jamais un autre nom que celui du patient en cours.
        9. Le nombre de type de document peut être supérieur à 1, il faut donc les lister tous.
        10. Chaque type de document correspond à un compte rendu médical, il faut donc les lister tous.
        ATTENTION: Si l'utilisateur pose une question de suivi ("il", "elle", "quel âge a-t-il ?"), réfère-toi au patient déjà identifié.
        11. DOUBLONS : Si plusieurs patients portent le même nom, l'ID fourni par l'utilisateur est prioritaire et déterminant. Ne jamais ignorer un ID explicitement mentionné.
        12. L'âge est déjà exprimé en années, affiche-le directement.
        13. DURÉE DE SÉJOUR : Affiche la valeur telle quelle en utilisant l'unité "jours".

        CONTEXTE :
        {contexte}"""


    # PROMPT AVEC AJOUT DE MEMOIRE !!
    # prompt = ChatPromptTemplate.from_messages([SystemMessage(content=systeme_prompt), MessagesPlaceholder(variable_name="history"),("human", "{question}")])
    prompt = ChatPromptTemplate.from_messages([("system", systeme_prompt), MessagesPlaceholder(variable_name="history"),("human", "{question}")])

    chaine = prompt | llm | StrOutputParser()

    # --- Interface ---
    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
    with col1:
        st.image("Images/logo_limics.png", width=300)
    with col3:
        st.image("Images/Logo_of_Sorbonne_University.png", width=150)
    with col4:
        st.image("Images/Logo_Polytech_Sorbonne.png", width=150)

    st.markdown("---")
    st.subheader("🤖 Chatbot basé sur un dossier patient ")
    st.markdown("**Objectif** : Répondre à des questions sur un dossier patient en langage naturel.")
    st.markdown("**Représentation** : Fichier JSON.")
    st.markdown("**Informations** : Il est possible de demander des informations générales sur le dossier patient ou bien des informations précises.")
    st.markdown("**Remarque** : Veillez à toujours mentionner le nom du patient dans votre question. En cas de doublons, ajoutez l'ID.")
    st.markdown("---")
    st.subheader("Bonjour, je suis votre assitant médical !")

    # parcourt tous les messages issus de la session, pour l'affichage de la conversation
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["contenu"])

    # réinitialise la mémoire de la conversation pour questionner sur un autre patient, objectif : garder le llm focalisé sur un seul patient et donc un seul document à la fois
    col_reset, _ = st.columns([1, 5])
    with col_reset:
        if st.button("Changer de patient"):
            st.session_state.messages = []
            st.session_state.historique_llm = []
            st.session_state.document_courant = None
            st.session_state.patient_courant = None
            st.rerun()

    if question := st.chat_input("Posez votre question"):
    # idem à : question = st.chat_input("Posez votre question")
    # if question :

        # On ne recherche que si aucun document n'est encore fixé
        # On crée la clé du dico session_state si elle n'existe pas encore
        # Première question de la session
        if st.session_state.document_courant is None:

            resultats = rechercher_candidats(question, base_de_donnees, embedding)

            st.session_state.document_courant = resultats[0] # le meilleur résultat issu de la recherche devient alors le document sur lequel se base le modèle pour répondre aux requêtes utilisateur

            st.session_state.patient_courant = (resultats[0].get("name"),resultats[0].get("ID")) # on garde les infos permettant d'identifier le patient

        meilleur_resultat = st.session_state.document_courant
        resultats = [meilleur_resultat] # pour l'affichage des sources

        st.session_state.messages.append({"role": "user", "contenu": question})

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Recherche dans les documents cliniques..."):

                meilleur_resultat = st.session_state.document_courant
                resultats = [meilleur_resultat]

                contextes = [
                    f"--- Début du document médical ---\n"
                    f"ID: {meilleur_resultat.get('ID')}\n"
                    f"Spécialité: {meilleur_resultat.get('specialty')}\n"
                    f"Pool: {meilleur_resultat.get('pool')}\n"
                    f"Nom: {meilleur_resultat.get('name')}\n"
                    f"Age: {round(meilleur_resultat.get('age', 0) * 100)} ans\n" #je normalise directement ici mieux que le prompt
                    f"Sexe: {meilleur_resultat.get('sex')}\n"
                    f"Mode d'admission: {meilleur_resultat.get('admission_mode')}\n"
                    f"Mode de sortie: {meilleur_resultat.get('discharge_mode')}\n"
                    f"Type de soin: {meilleur_resultat.get('type_of_care')}\n"
                    f"Diagnostic principal: {', '.join(meilleur_resultat.get('primary_diagnosis', []))}\n"
                    f"Procédure principale: {', '.join(meilleur_resultat.get('primary_procedure', []))}\n"
                    f"Durée de séjour: {meilleur_resultat.get('length_of_stay')} jours\n"
                    f"Type de document: {', '.join(meilleur_resultat.get('Type', []))}\n"
                    f"En-tête: {', '.join(meilleur_resultat.get('header', []))}\n"
                    f"Compte-rendu: {', '.join(meilleur_resultat.get('text', []))}\n"
                    f"--- Fin du document ---\n"
                ]

                texte_contexte = "\n\n".join(contextes)

                reponse = chaine.invoke({
                    "contexte": texte_contexte,
                    "history": st.session_state.historique_llm,
                    "question": question
                })

                st.markdown(reponse)

                with st.expander("Sources utilisées"):
                    for i, res in enumerate(resultats, 1):
                        st.markdown(f"**Document {i} (Patient ID : {res.get('ID')} | Nom : {res.get('name')})**")
                        st.caption(str(res.get('specialty', '')))
                        st.caption(str(res.get('pool', '')))
                        st.caption(str(res.get('sex', '')))
                        st.caption(str(res.get('age', '')))
                        st.caption(str(res.get('admission_mode', '')))
                        st.caption(str(res.get('discharge_mode', '')))
                        st.caption(str(res.get('type_of_care', '')))
                        st.caption(str(res.get('Type', '')))
                        st.caption(str(res.get('header', '')))
                        st.caption(str(res.get('text', '')))
                        st.caption(str(res.get('primary_procedure', '')))
                        st.caption(str(res.get('primary_diagnosis', '')))
                        st.caption(str(res.get('length_of_stay', '')))

                # Mise à jour mémoire LangChain
                st.session_state.historique_llm.append(HumanMessage(content=question))
                st.session_state.historique_llm.append(AIMessage(content=reponse))

                # Sauvegarde message affichage (reponse est maintenant un str)
                st.session_state.messages.append({"role": "assistant", "contenu": reponse})

if __name__ == "__main__":
    main()
