====== Projet PARHAF ====== 

Le corpus PARHAF est un jeu de données de textes médicaux en français, conçu spécifiquement pour la recherche en traitement automatique des langues (TAL/NLP). Il
contient plusieurs milliers de comptes rendus cliniques décrivant des patients, couvrant un large éventail de spécialités médicales.

Sa particularité essentielle est qu’il ne contient aucune donnée réelle de patients : les cas ont été entièrement rédigés par des professionnels de santé (internes, médecins) à partir de scénarios cliniques réalistes mais fictifs.

Contrairement aux bases issues du système de santé réel, qui sont fortement contraintes et rarement accessibles, PARHAF est librement utilisable à des fins pédagogiques et de recherche, ce qui en fait un excellent terrain d’expérimentation.
Voici quelques propositions de projets à réaliser sur ce jeu de données.

====== Outil 1 : Chatbot basé sur un dossier patient =======
(Eliott Ramos-Gauthier, Alma Lemansour, Lamia Bouhous, étudiant.e.s-ingénieur.e.s à Polytech Sorbonne, MAIN)

+ fichier JSON

Ce système RAG permet d'interroger en langage naturel le corpus PARHAF, structuré au format JSON pour une analyse précise des dossiers patients.
Il offre la flexibilité de poser des questions aussi bien générales que ciblées sur le suivi médical.
Note importante : Pour garantir la précision des résultats, veuillez toujours mentionner le nom du patient dans votre requête ; en cas d'homonymie, 
précisez également son ID.
Dès que vous souhaitez changer de patient, il suffit d'appuyer sur le bouton prévu pour réinitialiser la mémoire.

====== Outil 2 : Recherche de patients avec un RAG =======
...

====== Outil 3 : Recherche de patients similaires =======
(Eliott Ramos-Gauthier, étudiant-ingénieur à Polytech Sorbonne, MAIN)
+ fichier JSON

Cet outil a été conçu pour identifer et extraire à partir du corpus PARHAF, la cohorte des 100 patients présentant le profil le plus similaire au patient cible sélectionné.

Objectif : Retrouver les patients dont les caractéristiques cliniques sont les plus proches du patient de référence.

Représentation des données : L'analyse s'appuie sur une structure de données au format JSON.

Ensemble fermé : Les données catégorielles (ex: spécialité, sexe) sont comparées par correspondance stricte, attribuant un score binaire de 0 (différent) ou 1 (identique).

Ensemble vectoriel : Les attributs complexes (ex: textes, admission) sont comparés via le cosinus normalisé de leurs représentations vectorielles, générant un score de similarité compris entre 0 et 1

Score de similarité : Le résultat global est calculé comme la moyenne pondérée des scores obtenus sur l'ensemble des attributs que vous avez sélectionnés, vous permettant ainsi d'ajuster l'importance de chaque critère dans la recherche.

Afin d'offrir une vision d'ensemble sur le corpus PARHAF, des graphiques sont mis à disposition sur les éléments fermés de la base de données.

Ces indicateurs clés ont été sélectionnés pour permettre d'appréhender rapidement la structure de la cohorte selon des variables structurantes telles que l'âge, la spécialité médicale, ou encore le mode d'admission. Ces visualisations constituent une première étape nécéssaire pour comprendre la distribution et le profil type des patients avant d'utiliser l'outil de similarité.

====== Outil 4 : Simplification de texte médical à destination des patients =======
...

====== Outil 5 : Complétion de texte médical =======
...

====== Outil 6 : Extraction structurée d’information clinique =======
(Lamia Bouhous, étudiante-ingénieure à Polytech Sorbonne, MAIN)

+ fichier JSON 

Main6 : Ce projet consiste à implémenter un programme permettant de structurer de manière lisible et intelligente un texte brut correspondant à un compte-rendu
patient. Pour ce faire, on récupère du jeu de données HuggingFace, les `id` et `compte-rendu` pour chaque ligne (= patient). 
Ces attributs sont structurés dans un fichier .json source par la fonction `CreerJson.py`.
Le `main6.py` implémenté ici consiste en l'utilisation d'un LLM (modèle `llama3.2` de Ollama) que je prompte pour qu'il extraie les informations les plus pertinentes.
Dans ce même prompt, je donne la structure (json) souhaité en sortie. Finalement, on obtient un fichier `extractions.json`.

====== Outil 7 : Timeline médicale (structuration temporelle =======
(Alma Lemansour, étudiante-ingénieure à Polytech Sorbonne, MAIN)
pas de fichier JSON 

Main7 : fait appel aux fonctions présentes dans outil7.
L'objectif est de créer une frise chronologique des évènements clés à partir de l'identifiant d'un patient. 
. extraction.py retourne sous format json les évènements clés appartenant à une liste précise de types, chacun possédant une date non nulle, un indexe de priorité, un indice de priorité (corresondant à l'ordre chronologique logique (antécédants avant diagnostic par exemple)), le type et numéro de compte rendu, et enfin l'ordre d'apparition de l'évènement dans le texte (en cas d'évènements de même date et indice de priorité). 
. tri.py trie les évènements chronologiquement, selon l'ordre : n° de compte rendu --> date --> indice de priorité --> ordre d'apparition.
Cela permet de relier les différents comptes rendus entre eux pour les patients en possédant plusieurs. 
. frise.py trace la frise chronologique grâce à la bibliothèque plotly (adapté pour les graphiques dynamiques).

====== Lancement de l'application ======

Le projet PARHAF s'articule autour de 7 outils informatiques permettant de mettre en valeur le corpus.
Chaque outil est relié à une page d'accueil, facilitant ainsi la navigation entre les différentes fonctionnalités.

Emplacement : Projet_PARHAF/Code/
Commande : streamlit run main.py

====== Remarques importantes =======

- Il est nécéssaire d'avoir llama3.2 et mistral.nemo d'installé sur l'ordinateur. 
	- ollama install llama3.2
	- ollama install mistral-nemo

- Il est nécéssaire d'avoir la dernière python (minimum python 3.10) d'installé sur l'ordinateur.

- Il est nécéssaire d'installé plusieurs biblitohtèques pyhton :
	- SentenceTransformer
	- Numpy
	- Matplotlib.pyplot
	- Streamlit
	- Plotly
	- Datetime
	- Langchain
	- Pandas
	- Seaborn
	
- Certains outils nécessitent des fichiers JSON volumineux. Afin d'optimiser le transfert et d'alléger le dépôt, ces fichiers ne sont pas inclus.
Il est nécessaire d'exécuter les outils une première fois depuis la page principale pour générer automatiquement les fichiers JSON requis.

====== Architecture ======

Code/
├── corpus_PARHAF_outil_1.json 
├── corpus_PARHAF_outil_3.json
├── corpus_PARHAF_outil_6.json
├── Images/
│   ├── logo_limics.png
│   ├── Logo_of_Sorbonne_University.png
│   └── Logo_Polytech_Sorbonne.png
├── main.py 
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
    │   ├── Vectoriser_document.py
    │ 
    ├── outil_3/
    │   ├── Attributs_document.py
    │   ├── Classe.py
    │   ├── Sauvegarde_fichier.py
    |   └── Vectoriser_document.py
    ├── outil_6/
    │   ├── CreerJson.py
    │   └── extractions.json
    └── outil_7/
        ├── extraction.py
        ├── frise.py
        └── tri.py
