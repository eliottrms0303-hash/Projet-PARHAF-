import streamlit as st
import json
import os
import sys
import pandas as pd
import numpy as np
from itertools import cycle
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.outil_3.Attributs_document import attributs_document
from src.outil_3.Classe import CaracteristiquesDocument
from src.outil_3.Vectoriser_document import vectoriser_documents
from src.outil_3.Sauvegarde_fichier import sauvegarder_documents



#-----------------------------------------------------------
#------ Fonction permettant de calculer la similarité ------
#-----------------------------------------------------------

def score_similarite(patient_cible, candidat, liste_attributs_selectionnees, coeff) :

    #------ Déclaration d'une variable pour stocker le score ------
    score_final = []
    
    #------ Déclaration des éléments fermés -------
    attributs_fermes = ["specialty", "pool", "sex", "admission_mode", "discharge_mode", "Type"]

    attributs_norm = ["age", "length_of_stay"]

    nom_attributs_traduction = {

    "Spécialité médicale" : "specialty",
    "Groupe patients ~ pool" : "pool",
    "Age" : "age",
    "Sexe" : "sex",
    "Mode d'admission" : "admission_mode",
    "Mode de sortie" : "discharge_mode",
    "Type de soins" : "type_of_care",
    "Type du document clinique" : "Type",
    "En-tête du document clinique" : "header",
    "Commentaires médicales du document clinique" : "text",
    "Procédure principale" : "primary_procedure",
    "Diagnostic principal" : "primary_diagnosis",
    "Durée du séjour" : "length_of_stay",
    }

    
    for nom_traduit in liste_attributs_selectionnees :
        
        cle_json = nom_attributs_traduction.get(nom_traduit)
        coeff_json = coeff.get(nom_traduit)

        #------ Cas attribut fermé ------
        if cle_json in attributs_fermes :
            
            if patient_cible.get(cle_json) == candidat.get(cle_json) :
                score_final.append(1.0)
            else :
                score_final.append(0.0)

        elif cle_json in attributs_norm :
            diff = patient_cible.get(cle_json) - candidat.get(cle_json)
            score_final.append(np.exp(-(diff**2)/(2*(0.5)**2)))
        
        #------ Cas attribut vectoriel ------
        else :

            vecteur_cible = patient_cible.get("vecteur", {}).get(cle_json)
            vecteur_candidat = candidat.get("vecteur", {}).get(cle_json)

            if vecteur_cible and vecteur_candidat :
                
                v1, v2 = np.array(vecteur_cible), np.array(vecteur_candidat)
                norme1, norme2 = np.linalg.norm(v1), np.linalg.norm(v2)
                
                if norme1 > 0 and norme2 > 0 :
                    
                    cos = np.dot(v1, v2) / (norme1 * norme2)
                    score = (cos + 1)/2
                    score_final.append(float(score))
                else :
                    score_final.append(0.0)
            else :
                score_final.append(0.0)
                    
    return score_final




#-------------------
#------- MAIN ------
#-------------------

def main():

    nom_fichier = "corpus_PARHAF_outil_3.json"
    
    if os.path.exists(nom_fichier) :
        print(f"Le fichier {nom_fichier} existe. Pas besoin de le recalculer.")
    else :
        print(f"Traitement du corpus PARHAF en cours...")
        mes_documents = attributs_document()

        print(f"Vectorisation des attributs...")
        vectoriser_documents(mes_documents)

        print(f"Sauvegarde du corpus...")
        sauvegarder_documents(mes_documents, nom_fichier)


    #------ Chargement des données ------
    @st.cache_data
    def charger_base_de_donnees():
        with open('corpus_PARHAF_outil_3.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    base_de_donnees = charger_base_de_donnees()



    #------ Configuration de la page ------
    st.set_page_config(page_title = "Recherche de patients", layout = "wide")

    #------ Logo haut de page ------
    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
    with col1 :
        st.image("Images/logo_limics.png", width=300)
    with col3 :
        st.image("Images/Logo_of_Sorbonne_University.png", width=150)
    with col4 :
        st.image("Images/Logo_Polytech_Sorbonne.png", width=150)

    col5, col6 = st.columns([3,3])
    with col6 :
        st.markdown("***Outil proposé par Eliott Ramos-Gauthier, étudiant-ingénieur à Polytech Sorbonne - MAIN***")

    #------ Trait horizontal ------
    st.markdown("---")


    #------ Titre ------
    st.subheader("👥 Recherche de patients similaires")

    #------ Explication ------
    st.markdown("Cet outil a été conçu pour identifer et extraire à partir du corpus PARHAF, la cohorte des 100 patients présentant le profil le plus similaire au patient cible sélectionné.")
    st.markdown("**Objectif** : Retrouver les patients dont les caractéristiques cliniques sont les plus proches du patient de référence.")
    st.markdown("**Représentation des données** : L'analyse s'appuie sur une structure de données au format JSON.")
    st.markdown("**Ensemble fermé** : Les données catégorielles (ex: spécialité, sexe) sont comparées par correspondance stricte, attribuant un score binaire de 0 (différent) ou 1 (identique).")
    st.markdown("**Ensemble vectoriel** : Les attributs complexes (ex: textes, admission) sont comparés via le cosinus normalisé de leurs représentations vectorielles, générant un score de similarité compris entre 0 et 1")
    st.markdown("**Score de similarité** : Le résultat global est calculé comme la moyenne pondérée des scores obtenus sur l'ensemble des attributs que vous avez sélectionnés, vous permettant ainsi d'ajuster l'importance de chaque critère dans la recherche. ")

    #------ Trait horizontal ------
    st.markdown("---")

    #------ DataFrame de la base de données ------
    df = pd.DataFrame(base_de_donnees)

    #------ Gaphique ~ Age ------
    df['age_tranche'] = pd.cut(df['age'] * 100, bins=range(0, 110, 10), labels=[f"{i}-{i+9}" for i in range(0, 100, 10)])
    pyramide_df = df.groupby(['age_tranche', 'sex']).size().unstack(fill_value=0)
    pyramide_df['F'] = - pyramide_df['F']
    fig_age, ax = plt.subplots(figsize=(6,4))
    pyramide_df[['F', 'M']].plot(kind='barh', stacked=True, color=['gold', 'steelblue'], ax=ax)
    ax.set_title("Répartition de la cohorte par âge et sexe")
    ax.set_xlabel("Nombre de patients")
    ax.set_ylabel("Tranche d'âge")
    ax.legend(['Femmes', 'Hommes'])
    ax.axvline(0, color='black', linewidth=1)


    #------ Graphique ~ Specialty
    pyramide_df = df.groupby(['specialty', 'sex']).size().unstack(fill_value=0)
    pyramide_df['F'] = - pyramide_df['F']
    fig_specialty, ax = plt.subplots(figsize=(7, 5))
    pyramide_df[['F', 'M']].plot(kind='barh', stacked=True, color=['gold', 'steelblue'], ax=ax)
    ax.set_title("Répartition de la cohorte par spécialité et sexe")
    ax.set_xlabel("Nombre de patients")
    ax.set_ylabel("Spécialité")
    ax.legend(['Femmes', 'Hommes'])
    ax.axvline(0, color='black', linewidth=1)

    #------ Graphique ~ Durée de séjour ------
    fig_length, ax = plt.subplots(figsize=(6, 4))
    sns.boxplot(
        data=df, 
        x='sex', 
        y='length_of_stay', 
        hue='sex', 
        palette=['steelblue', 'gold'], 
        legend=False,
        ax=ax
        )
    ax.set_title("Répartition de la durée de séjour par sexe")
    ax.set_xlabel("Sexe")
    ax.set_ylabel("Durée de séjour (jours)")
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    #------ Gaphique ~ Pool ------
    pyramide_df = df.groupby(['pool', 'sex']).size().unstack(fill_value=0)
    pyramide_df['F'] = - pyramide_df['F']
    fig_pool, ax = plt.subplots(figsize=(8, 6))
    pyramide_df[['F', 'M']].plot(kind='barh', stacked=True, color=['gold', 'steelblue'], ax=ax)
    ax.set_title("Répartition de la cohorte par Pool et sexe")
    ax.set_xlabel("Nombre de patients")
    ax.set_ylabel("Pool")
    ax.legend(['Femmes', 'Hommes'])
    ax.axvline(0, color='black', linewidth=1)

    #------ Graphique ~ Admission mode -------
    pyramide_df = df.groupby(['admission_mode', 'sex']).size().unstack(fill_value=0)
    pyramide_df['F'] = - pyramide_df['F']
    fig_adm, ax = plt.subplots(figsize=(7, 5))
    pyramide_df[['F', 'M']].plot(kind='barh', stacked=True, color=['gold', 'steelblue'], ax=ax)
    ax.set_title("Répartition de la cohorte par Mode d'admission et sexe")
    ax.set_xlabel("Nombre de patients")
    ax.set_ylabel("Mode d'admission")
    ax.legend(['Femmes', 'Hommes'])
    ax.axvline(0, color='black', linewidth=1)
    

    #------ Graphique ~ Discharge mode -------
    pyramide_df = df.groupby(['discharge_mode', 'sex']).size().unstack(fill_value=0)
    pyramide_df['F'] = - pyramide_df['F']
    fig_dsc, ax = plt.subplots(figsize=(5, 3))
    pyramide_df[['F', 'M']].plot(kind='barh', stacked=True, color=['gold', 'steelblue'], ax=ax)
    ax.set_title("Répartition de la cohorte par Mode de sortie et Sexe")
    ax.set_xlabel("Nombre de patients")
    ax.set_ylabel("Mode de sortie")
    ax.legend(['Femmes', 'Hommes'])
    ax.axvline(0, color='black', linewidth=1)


    #------ Affichage graphiques ------
    st.subheader("📊 Informations générales sur la cohorte")
    st.markdown(""" Afin d'offrir une vision d'ensemble sur le corpus PARHAF, des graphiques sont mis à disposition sur
                les éléments fermés de la base de données.""")
    st.markdown("""Ces indicateurs clés ont été sélectionnés pour permettre d'appréhender rapidement la structure de la cohorte
               selon des variables structurantes telles que l'âge, la spécialité médicale, ou encore le mode d'admission.
               Ces visualisations constituent une première étape nécéssaire pour comprendre la distribution et le profil type des patients
               avant d'utiliser l'outil de similarité.
               """)

    tabs = st.tabs([
        "Âge & Durée de séjour",
        "Spécialité & Pool",
        "Mode d'admission",
        "Mode de sortie",
        ])

    with tabs[0] :
        col_a, col_b = st.columns(2)
        with col_a :
            col_a = st.pyplot(fig_age)
            col_a = plt.close(fig_age)
        with col_b :
            col_b = st.pyplot(fig_length)
            col_b = plt.close(fig_length)

    with tabs[1] :
        col_c, col_d = st.columns(2)
        with col_c :
            col_c = st.pyplot(fig_specialty)
            col_c = plt.close(fig_specialty)
        with col_d :
            col_d = st.pyplot(fig_pool)
            col_d = plt.close(fig_pool)

    with tabs[2] :
        st.pyplot(fig_adm)
        plt.close(fig_adm)

    with tabs[3] :
        st.pyplot(fig_dsc)
        plt.close(fig_dsc)
        

    


    #------ Sélection du patient cible ~ Menu déroulant ------
    st.subheader("1 - 🎯 Sélection du patient cible")
    st.markdown("""Choisissez le patient de référence dans le menu déroulant.
                Le système utilise son identifiant unique (ID) et son nom complet.
                """)
    liste_nom_patients = [f"{p['ID']} - {p['name']}" for p in base_de_donnees]
    patient_choisi = st.selectbox("", liste_nom_patients)


    #------ Récupération du patient cible ------
    
    patient_cible = None
    for patient in base_de_donnees :
        if f"{patient['ID']} - {patient['name']}" == patient_choisi :
            patient_cible = patient
            break
                    

    #------ Sélection des attributs sur lesquels effectuer la similarité ------
    st.subheader("2 - ⚖️ Sélection des attributs et pondération")
    st.markdown("""Sélectionnez les attributs que vous souhaitez inclure dans l'analyse de similarité.
                Pour chaque attribut retenu, un curseur vous permet de définir un coefficient, afin
                de définir le poids de ces derniers. 
                """)

    coeff = {}

    liste_noms_attributs_classe = [
        "Spécialité médicale",
        "Groupe patients ~ pool",
        "Sexe",
        "Age",
        "Mode d'admission",
        "Mode de sortie",
        "Type de soins",
        "Type du document clinique",
        "En-tête du document clinique",
        "Commentaires médicales du document clinique",
        "Procédure principale",
        "Diagnostic principal",
        "Durée du séjour",
        ]

    coeff = {}
    
    cols = st.columns(3)
    
    for i, attr in enumerate(liste_noms_attributs_classe):
        with cols[i % 3]:
            with st.container(border=True):
                c = st.checkbox(attr, key=f"check_{attr}")
                if c:
                    coeff[attr] = st.slider(f"Poids : {attr}", 0.0, 1.0, 1.0, 0.1, key=f"slider_{attr}", label_visibility="collapsed")
                else:
                    coeff[attr] = 0.0

    #------- Récupération des attributs sélectionnés ------
    liste_attributs_selectionnes = [ nom for nom in liste_noms_attributs_classe if st.session_state.get(f"check_{nom}", False) ]
                     
    #------- Résultat de la recherche similarité ------
    st.subheader("3 - 📝 Résultat de la similarité")
    st.markdown("Une fois la recherche lancée, le moteur compare le patient cible à tous les autres profils de la base de données")
    st.markdown("**Calcul détaillé** : Chaque candidat reçoit un score global basé sur la moyenne pondérée de ses similarités par attribut.")
    st.markdown("**Classement** : Le système génère automatiquement une liste triée affichant les 100 profils les plus pertinents.")
    st.markdown("**Exportation** : Un bouton de téléchargement vous permet d'extraire immédiatement ces résultats sous format CSV.")
    
    col_btn1, col_btn2 = st.columns([1, 4])

    with col_btn1:
        lancer_recherche = st.button("Lancer la recherche")
        
    if lancer_recherche:
    
        if not patient_cible or not liste_attributs_selectionnes :
            st.warning("Veuillez sélectionner un patient et au moins un attribut.")
        
        else :
            #------ Déclaration d'une liste pour stocker tous les résultats
            resultats = []
            
            for candidat in base_de_donnees :
            
                if candidat.get("name") != patient_cible.get("name") :

                    scores_tous_attributs = score_similarite(patient_cible, candidat, liste_attributs_selectionnes, coeff)
    
                    poid_coeff = [coeff[attr] for attr in liste_attributs_selectionnes]
                    somme_poid = sum(poid_coeff)

                    if somme_poid > 0 :
                        score_final = sum(s * p for s, p in zip(scores_tous_attributs, poid_coeff)) / somme_poid
                    else :
                        score_final = 0.0
        
                    details_par_attribut = dict(zip(liste_attributs_selectionnes, scores_tous_attributs))
        
                    resultat_candidat = {
                        "Nom du patient": candidat.get("name"),
                        "ID du patient" : candidat.get("ID"),
                        "Score de similarité": round(float(score_final), 4)
                    }
                    resultat_candidat.update(details_par_attribut)
        
                    resultats.append(resultat_candidat)
                
            #------ Tri des 100 meilleurs profils similaires ------
            top_100 = sorted(resultats, key = lambda x : x["Score de similarité"], reverse=True)[:100]
        
            #------ Affichage -------
            st.success(f"Top 100 des patients les plus similaires à {patient_cible.get('name')} :")
            
            #------ Bouton de téléchargement dans la colonne adjacente ------
            with col_btn2:
                df_top100 = pd.DataFrame(top_100)
                st.download_button(
                    label="📥 Télécharger le Top 100 en format CSV",
                    data=df_top100.to_csv(index=False).encode('utf-8'),
                    file_name='resultats_similarite.csv',
                    mime='text/csv'
                )

            st.table(top_100)
          

if __name__ == "__main__":
    main()

