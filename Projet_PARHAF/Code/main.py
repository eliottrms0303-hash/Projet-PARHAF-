import streamlit as st
import subprocess

#-----------------------------------------------
#------ Streamlt principal ~ Page accueil ------
#-----------------------------------------------

def main() :

    #----- Nom page accueil ------
    st.set_page_config(page_title = "Accueil ~ Projet PARHAF", layout = "wide")

    #----- Affichage Logo ------
    col1, col2, col3, col4 = st.columns([4,1,1,1])
    with col1 :
        st.image("Images/logo_limics.png", width = 300)
    with col3 :
        st.image("Images/Logo_of_Sorbonne_University.png", width = 150)
    with col4 :
        st.image("Images/Logo_Polytech_Sorbonne.png", width = 150)

    #------ Trait horizontal ------
    st.markdown("---")

    #------ Qu'est ce que le coprus PARHAF ? ------
    st.subheader("Qu'est ce que le corpus PARHAF ?")

    text = '''Le corpus PARHAF est un jeu de données de textes médicaux en français,
                 conçu spécifiquement pour la recherche en traitement automatique des langues (TAL/NLP).
                 Il contient plusieurs milliers de comptes rendus cliniques décrivant des patients, couvrant un large éventail de spécialités médicales.
                 Sa particularité essentielle est qu’il ne contient aucune donnée réelle de patients : les cas ont été entièrement rédigés par des professionnels
                 de santé (internes, médecins) à partir de scénarios cliniques realistic mais fictifs. Cela permet de contourner les contraintes juridiques très fortes
                 liées aux données de santé tout en conservant un niveau de réalisme élevé. '''

    st.markdown(text)

    #------ Trait horizontal ------
    st.markdown("---")

    with st.expander("Chatbot basé sur un dossier patient") :
        st.write("**Objectif** : Construire un système capable de répondre à des questions en langage naturel à partir du dossier d’un patient ")
        st.write("***Outil proposé par Eliott Ramos-Gauthier, Alma Lemansour, Lamia Bouhous, étudiant·e·s-ingénieur·e·s à Polytech Sorbonne, MAIN***")
        if st.button("Aller vers l'outil", key="btn1", use_container_width=True) :
            st.switch_page("pages/main1.py")

    with st.expander("Recherche de patients avec un RAG") :
        st.write("**Objectif** : ... ")
        st.button("Aller vers l'outil", key="btn2", use_container_width=True)

    with st.expander("Recherche de patients similaires") :
        st.write("**Objectif** : Étant donné un dossier patient, retrouver les patients les plus similaires.")
        st.write("***Outil proposé par Eliott Ramos-Gauthier, étudiant-ingénieur à Polytech Sorbonne, MAIN***")
        if st.button("Aller vers l'outil", key="btn3", use_container_width=True) :
            st.switch_page("pages/main3.py")

    with st.expander("Simplification de texte médical à destination des patients") :
        st.write("**Objectif** : ... ")
        st.button("Aller vers l'outil", key="btn4", use_container_width=True)

    with st.expander("Complétion de texte médical") :
        st.write("**Objectif** : ... ")
        st.button("Aller vers l'outil", key="btn5", use_container_width=True)

    with st.expander("Extraction structurée d’information clinique") :
        st.write("**Objectif** :  Transformer un texte libre en structure exploitable (type JSON). ")
        st.write("***Outil proposé par Lamia Bouhous, étudiante-ingénieure à Polytech Sorbonne, MAIN***")
        if st.button("Aller vers l'outil", key="btn6", use_container_width=True) :
            st.switch_page("pages/main6.py")

    with st.expander("Timeline médicale") :
        st.write("**Objectif** : Reconstruire une chronologie des événements médicaux. ")
        st.write("***Outil proposé par Alma Lemansour, étudiante-ingénieure à Polytech Sorbonne, MAIN***")
        if st.button("Aller vers l'outil", key="btn7", use_container_width=True) :
            st.switch_page("pages/main7.py")

        
        
    

if __name__ == "__main__":
    main()

    
