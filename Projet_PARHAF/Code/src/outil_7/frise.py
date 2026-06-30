import plotly.graph_objects as go #bibliothèque pour créer des graphiques interactifs
from datetime import datetime
#nb pour moi: on utilise pas matplotlib qui génère des graphiques statiques

# FONCTIONS UTILITAIRES

def parse_date(date_str):
    """Convertit 'AAAA/MM/JJ' en datetime."""
    try:
        return datetime.strptime(date_str, "%Y/%m/%d")#transforme la date en objet datetime pour pouvoir trier les dates correctement.
    except (ValueError, TypeError):
        return None


# Ajouter des retours à la ligne tous les 60 caractères (pr la description quand elle est trop longue)
def couper_texte(texte, longueur=60):
    mots = texte.split(" ")
    lignes = []
    ligne_courante = ""
    for mot in mots:
        if len(ligne_courante) + len(mot) > longueur:
            lignes.append(ligne_courante.strip())
            ligne_courante = mot + " "
        else:
            ligne_courante += mot + " "
    lignes.append(ligne_courante.strip())
    return "<br>".join(lignes)

# COULEURS PAR TYPE D'ÉVÉNEMENT

COULEURS = {
    "Contexte":                 "#A8D8EA",
    "Antécédents":              "#FFCBA4",
    "Hospitalisation":          "#FF6B6B",
    "Consultation":             "#FFD93D",
    "Renseignements cliniques": "#C3F584",
    "Traitements entree":       "#6BCB77",
    "Examens paracliniques":    "#845EC2",
    "Traitements sortie":       "#4D8076",
    "Diagnostic":               "#FF9671",
    "Sortie":                   "#B0B0B0",
}

COULEUR_DEFAUT = "#DDDDDD" #utile pour le .get() dans le cas où un type d'événement n'est pas dans le dictionnaire COULEURS

# CONSTRUCTION DE LA FRISE
def construire_frise(timeline, id_patient):
    """Construit et affiche la frise chronologique avec Plotly."""

    # Préparation des données
    # L'axe X = position dans la liste (0, 1, 2, 3...) 
    # L'ordre est déjà garanti par le code de tri précédent, donc on peut juste utiliser l'index de la liste.
    positions_x = list(range(len(timeline)))
    #exemple pour 5 évènments : positions_x = [0, 1, 2, 3, 4] 
    #en gros chaque événement reçoit une position sur l'axe X. L'événement 0 est à gauche, l'événement 4 à droite, espacés uniformément.
    #len(timeline) = 5, range(len(timeline)) = range(5) = séquence de 0 à 4, list(range(len(timeline))) = [0, 1, 2, 3, 4]

    hover_texts = []
    couleurs    = []
    labels_date = []  # dates affichées sous chaque point

    for ev in timeline:
        type_ev = ev.get("type", "?")
        desc    = ev.get("description", "")
        type_cr = ev.get("type_cr_parhaf", "?")
        date    = ev.get("date", "?")

        couleurs.append(COULEURS.get(type_ev, COULEUR_DEFAUT))

        if date == "0000/00/00":
            labels_date.append("Antécédents")
        else:
            labels_date.append("/".join(date.split("/")[::-1])) # "2025/05/19" → split sur "/" → ["2025", "05", "19"] → inverser → "19/05/2025"
        date_affichee = "/".join(date.split("/")[::-1])

        # Texte qui app quand on pointe la souris sur un point de la frise
        hover = (
            f"<b>{type_ev}</b><br>" # <b> = gras,        <br> = saut de ligne
            f"Date : {date_affichee}<br>" #on affiche la date, puis saut de ligne
            f"CR : {type_cr}<br>"#on affiche le type de compte rendu, puis saut de ligne
            f"<br>{couper_texte(desc)}"#on affiche la description de l'événement (avec des retours à la ligne tous les 60 caractères pour que ce soit lisible)
        )
        hover_texts.append(hover) #on ajoute ce texte à la liste hover_texts, chaque événement aura son propre texte d'info-bulle.

    #  Ligne horizontale de la frise 
    trace_ligne = go.Scatter(
        x=positions_x, #bien une liste de positions sur l'axe X, chaque événement a sa position
        y=[0] * len(positions_x), #en, gros tous les y sont à 0 pour que la ligne soit horizontale, et pareil ici liste de même longueur que positions_x
        mode="lines", #slmt une ligne; markers = points, lines+markers = les deux
        line=dict(color="lightgrey", width=2), #couleur et épaisseur de la ligne
        hoverinfo="none", #pas d'info-bulle pour la ligne, on veut juste les points
        showlegend=False #la ligne n'apparaît pas dans la légende
    )

    #  Points par type (pour la légende)
    traces_points = []
    types_vus = {} #c'est un dictionnaire de dictionnaires, chaque type d'évènement a sa propre entrée avec ses coordonnées x, y, texte d'info-bulle et couleur. 

    for i, ev in enumerate(timeline):
        type_ev = ev.get("type", "?")
        if type_ev not in types_vus:
            # si ce type n'a pas encore de clé dans le dictionnaire → on la crée
            types_vus[type_ev] = {
                "x": [], "y": [], "hover": [],
                "couleur": COULEURS.get(type_ev, COULEUR_DEFAUT)
            }
        types_vus[type_ev]["x"].append(i)   # position dans la liste
        types_vus[type_ev]["y"].append(0)   #tous les y à 0
        types_vus[type_ev]["hover"].append(hover_texts[i]) #on ajoute le texte d'info-bulle correspondant à cet événement

    for type_ev, data in types_vus.items(): #pour chaque type d'événement, on crée un Scatter pour les points de ce type
        #.items() renvoie une vue des paires clé-valeur du dictionnaire, ici type_ev = clé (nom du type d'événement), data = valeur (dictionnaire avec x, y, hover et couleur)
        trace = go.Scatter(
            x=data["x"],
            y=data["y"],
            mode="markers", #cette fois on trace des points
            name=type_ev,
            marker=dict( #on crée un dictionnaire pour définir les propriétés des marqueurs (points)
                color=data["couleur"],
                size=16,#taille des points
                line=dict(color="white", width=2)#représente le contour des points, ici blanc et épaisseur 2
            ),
            text=data["hover"],
            hovertemplate="%{text}<extra></extra>", #remplace le texte d'info-bulle par le texte qu'on a défini dans data["hover"], <extra></extra> supprime la boîte supplémentaire automotique par plotly qui affiche le nom de la trace
        )
        traces_points.append(trace)

    # Annotations : date affichée sous chaque point pour avoir l'effet de frise chronologique
    annotations = []
    for i, date in enumerate(labels_date):
        annotations.append(dict(
            x=i,
            y=-0.08, #un peu en dessous de la ligne (y=0), 
            text=date,
            showarrow=False, #on ne veut pas de flèche pour ces annotations, juste le texte
            font=dict(size=9, color="grey"),# taille et couleur du texte
            textangle=-45,#angle du texte pour qu'il soit lisible même si les dates sont proches
        ))

    # Mise en page
    layout = go.Layout( #definit l'apparence générale du graphique
        title=dict(
            text=f"Timeline médicale — Patient {id_patient}",
            font=dict(size=18),
            x=0.5,        # ← centre le titre
            xanchor="center"
        ), #dict() permet de définir un dictionnaire
        xaxis=dict(
            showgrid=False, # pas de lignes de grille verticales
            showticklabels=False,  # on gère les dates avec les annotations, pas besoin des ticks automatiques
            zeroline=False,#pas de trait vertical à x=0
            range=[-1, len(timeline) + 0.5],  # un peu de marge de chaque côté (-1 à gauche, len(timeline) + 0.5 à droite car fleche au bout)
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False, #pas de trait horizontal à y=0
            range=[-0.3, 0.3],
        ),
        legend=dict(
            orientation="h", #horizontal, sinon vertical par défaut
            yanchor="bottom", # ancrage vertical de la légende en bas
            y=1.05,# position Y : au dessus du graphique (1 = tout en haut)
            xanchor="center",  # ← centre la légende
            x=0.5             # ← au milieu
        ),
        hovermode="closest",# au survol, montre l'info du point le plus proche de la souris
        plot_bgcolor="white",#fond du graphique en 
        height=400, #hauteur du graphique en pixels
        autosize=True,         #  la frise prend toute la largeur disponible, pr que ce soit centré sur la page web!
        margin=dict(l=20, r=40, t=100, b=100), #marges autour du graphique (left, right, top, bottom)

        hoverlabel=dict(
        bgcolor="white",       # fond blanc
        font_size=12,
        font_color="black",
        bordercolor="grey",
        namelength=0,          # pas de nom de trace dans le hover
        align="left",          # texte aligné à gauche
        )
    )

    fig = go.Figure(
        data=[trace_ligne] + traces_points, #on combine la ligne horizontale et ensuite tous les points pas type d'evnmt par dessus
        layout=layout #mise en page définie juste avant
    )

    fig.update_layout(annotations=annotations) #update_layout permet de modifier la mise en page après la création de la figure, ici on ajoute les annotations

    # Flèche à la fin de la frise
    # Flèche centrée sur toute la largeur de la frise
    fig.add_annotation(
         x=len(timeline),    # dépasse légèrement le dernier événement
         y=0,
         ax=-0.5,            # part d'avant le premier événement
         ay=0,
         xref="x", yref="y",
         axref="x", ayref="y",
         showarrow=True,
         arrowhead=2,
         arrowsize=1.5,
         arrowwidth=2,
         arrowcolor="lightgrey"
)

    return fig
