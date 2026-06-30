from datetime import datetime

def parse_date(date_str):
    """Convertit 'AAAA/MM/JJ' en datetime --> nécessaire pour le tri. Renvoie une date lointaine si invalide histoire d'avoir une date."""
    if date_str == "0000/00/00":
        return datetime(1, 1, 1)  # date minimale correspondant au type "Antécédents"→ toujours en premier
    try:
        return datetime.strptime(date_str, "%Y/%m/%d")
    except (ValueError, TypeError):
        return datetime(9999, 12, 31)


def filtrer_evenements(evenements):
    """Supprime les événements sans description."""
    filtred_evenements = []
    for ev in evenements:
        if ev.get("description", "") != "":
            filtred_evenements.append(ev) #on garde uniquement les descriptions non vides
    return filtred_evenements


def trier_evenements(evenements):
    """Trie selon : numéro CR → date → priorité (si dates identiques)→ ordre d'apparition (si dates et priorités identiques)."""
    return sorted(evenements, key=lambda ev: (
        ev.get("num_cr_parhaf", 0),
        parse_date(ev.get("date", "")),
        ev.get("index_priorite", 99),
        ev.get("ordre_apparition", 0),
    ))

def fusionner_evenements(timeline):
    """Regroupe en un seul événement ceux qui ont la même date ET le même type (plus facile à lire)."""
    
    fusionnes = []
    
    for ev in timeline:
        date_ev = ev.get("date", "")
        type_ev = ev.get("type", "")
        
        # On cherche si un événement avec même date et même type existe déjà
        trouve = False
        for ev_existant in fusionnes:
            if ev_existant.get("date") == date_ev and ev_existant.get("type") == type_ev:
                # On ajoute la description à l'événement existant
                ev_existant["description"] += " | " + ev.get("description", "")
                trouve = True
                break
        
        # Si aucun événement similaire trouvé, on ajoute normalement
        if not trouve:
            fusionnes.append(ev)
    
    return fusionnes


def trier_et_filtrer(evenements):
    """Filtre, trie puis fusionne les doublons de même date et type."""
    timeline = trier_evenements(filtrer_evenements(evenements))
    timeline = fusionner_evenements(timeline)  # ← nouveau
    return timeline
