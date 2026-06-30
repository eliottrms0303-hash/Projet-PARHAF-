# Projet PARHAF

Le corpus PARHAF est un jeu de données de textes médicaux en français, conçu spécifiquement pour la recherche en traitement automatique des langues (TAL/NLP). Il contient plusieurs milliers de comptes rendus cliniques décrivant des patients, couvrant un large éventail de spécialités médicales.

Sa particularité essentielle est qu’il ne contient aucune donnée réelle de patients : les cas ont été entièrement rédigés par des professionnels de santé (internes, médecins) à partir de scénarios cliniques réalistes mais fictifs.

Contrairement aux bases issues du système de santé réel, qui sont fortement contraintes et rarement accessibles, PARHAF est librement utilisable à des fins pédagogiques et de recherche, ce qui en fait un excellent terrain d’expérimentation.

---

## Liste des outils 

### Outil 1 : Chatbot basé sur un dossier patient
**Étudiant.e.s :** Eliott Ramos-Gauthier, Alma Lemansour, Lamia Bouhous (Polytech Sorbonne, MAIN)  
**Format :** Fichier JSON

Ce système RAG permet d'interroger en langage naturel le corpus PARHAF, structuré au format JSON pour une analyse précise des dossiers patients. Il offre la flexibilité de poser des questions aussi bien générales que ciblées sur le suivi médical.

*Note importante :* Pour garantir la précision des résultats, veuillez toujours mentionner le nom du patient dans votre requête ; en cas d'homonymie, précisez également son ID. Dès que vous souhaitez changer de patient, il suffit d'appuyer sur le bouton prévu pour réinitialiser la mémoire.

### Outil 2 : Recherche de patients avec un RAG
*(En cours)*

### Outil 3 : Recherche de patients similaires
**Étudiant :** Eliott Ramos-Gauthier (Polytech Sorbonne, MAIN)  
**Format :** Fichier JSON

Cet outil a été conçu pour identifier et extraire, à partir du corpus PARHAF, la cohorte des 100 patients présentant le profil le plus similaire au patient cible.

- **Objectif :** Retrouver les patients dont les caractéristiques cliniques sont les plus proches.
- **Ensemble fermé :** Les données catégorielles (ex: spécialité, sexe) sont comparées par correspondance stricte, attribuant un score binaire de 0 (différent) ou 1 (identique).
- **Ensemble vectoriel :** Les attributs complexes (ex: textes, admission) sont comparés via le cosinus normalisé de leurs représentations vectorielles, générant un score de similarité compris entre 0 et 1.
- **Score de similarité :** Le résultat global est calculé comme la moyenne pondérée des scores obtenus sur l'ensemble des attributs sélectionnés.

*Visualisation :* Afin d'offrir une vision d'ensemble sur le corpus PARHAF, des graphiques sont mis à disposition sur les éléments fermés de la base de données. Ces indicateurs clés permettent d'appréhender rapidement la structure de la cohorte (âge, spécialité, mode d'admission).

### Outil 4 : Simplification de texte médical à destination des patients
*(En cours)*

### Outil 5 : Complétion de texte médical
*(En cours)*

### Outil 6 : Extraction structurée d’information clinique
**Étudiante :** Lamia Bouhous (Polytech Sorbonne, MAIN)  
**Format :** Fichier JSON

Ce projet consiste à structurer de manière lisible un texte brut correspondant à un compte-rendu patient. Le programme utilise un LLM (`llama3.2` de Ollama) pour extraire les informations pertinentes selon une structure JSON définie, générant ainsi un fichier `extractions.json`.

### Outil 7 : Timeline médicale (structuration temporelle)
**Étudiante :** Alma Lemansour (Polytech Sorbonne, MAIN)  
**Format :** Pas de fichier JSON spécifique

L'objectif est de créer une frise chronologique des évènements clés à partir d'un identifiant patient.
- `extraction.py` : extrait les évènements clés avec date et indice de priorité.
- `tri.py` : trie les évènements chronologiquement.
- `frise.py` : trace la frise chronologique grâce à la bibliothèque Plotly.

---

## Lancement de l'application

Le projet PARHAF s'articule autour de 7 outils accessibles via une interface unifiée.

- **Emplacement :** `Projet_PARHAF/Code/`
- **Commande :** `streamlit run main.py`

---

## Remarques importantes

- **Prérequis :**
  - Installation de `llama3.2` et `mistral-nemo` via `ollama install`.
  - Python 3.10 minimum requis.
  - Bibliothèques nécessaires : `SentenceTransformer`, `Numpy`, `Matplotlib`, `Streamlit`, `Plotly`, `Datetime`, `Langchain`, `Langchain_OpenAI`, `Pandas`, `Seaborn`.

- **Gestion des fichiers JSON :**
  Certains outils nécessitent des fichiers JSON volumineux. Afin d'optimiser le transfert et d'alléger le dépôt, ces fichiers ne sont pas inclus. Vous devez lancer les outils une première fois depuis la page principale pour générer automatiquement les fichiers JSON requis.

---

## Architecture

```text
Code/
├── corpus_PARHAF_outil_1.json 
├── corpus_PARHAF_outil_3.json
├── corpus_PARHAF_outil_6.json
├── main.py 
├── Images/
│   ├── logo_limics.png
│   ├── Logo_of_Sorbonne_University.png
│   └── Logo_Polytech_Sorbonne.png
├── pages/
│   ├── main1.py
│   ├── main3.py
│   ├── main6.py
│   └── main7.py
└── src/ 
    ├── outil_1/
    │   ├── Attributs_document.py
    │   ├── Classe.py
    │   ├── Sauvegarde_fichier.py
    │   └── Vectoriser_document.py
    ├── outil_3/
    │   ├── Attributs_document.py
    │   ├── Classe.py
    │   ├── Sauvegarde_fichier.py
    │   └── Vectoriser_document.py
    ├── outil_6/
    │   ├── CreerJson.py
    │   └── extractions.json
    └── outil_7/
        ├── extraction.py
        ├── frise.py
        └── tri.py
