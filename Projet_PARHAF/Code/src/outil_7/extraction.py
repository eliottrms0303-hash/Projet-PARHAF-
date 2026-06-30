import json
import time

def extraire_evenements(id_patient, patients_parhaf, chaine_extraction):
    """Extrait les événements d'un patient et retourne la liste brute."""

    types_autorises = {
        "Contexte": 0,
        "Antécédents": 0,
        "Hospitalisation": 1,
        "Consultation": 1,
        "Renseignements cliniques": 1,
        "Traitements entrée": 2,
        "Examens paracliniques": 3,
        "Traitements sortie": 4,
        "Diagnostic": 5,
        "Sortie": 6
    }

    mots_interdits = [
        "MACROSCOPIE", "MICROSCOPIE", "PRESCRIPTEUR",
        "FRAGMENTS", "ALLERGIE", "MODE DE VIE"
    ]

    tous_les_evenements_du_patient = []
    patient_trouve = False

    for patient in patients_parhaf:
        # On ignore tous les patients qui ne correspondent pas à l'id demandé
        if str(patient["id"]).upper() != id_patient:
            continue

        # Si on arrive ici, c'est qu'on a trouvé le bon patient
        patient_trouve = True
        documents_patient = patient.get("documents", {}) # on récupère les documents du patient
        liste_textes = documents_patient.get("text", []) # textes des comptes rendus
        liste_types = documents_patient.get("type", []) # types des comptes rendus

        print(f"Patient {id_patient} trouvé ({len(liste_textes)} docs).") #on affiche le nombre de documents du patient (nbre de cr)

        for idx_doc, (type_cr, text_cr) in enumerate(zip(liste_types, liste_textes)):
        #zip (.,.): boucle sur 2 listes et assemble paire par paire
        #ici on parcourt en gros compte rendu par compte rendu

            try: #securité : si marche pas saute a except
                reponse = chaine_extraction.invoke({
                    "type_document": type_cr,
                    "texte_medical": text_cr
                })
                #chaine_extraction.invoke: appelle notre pipeline LangChain 
                #On lui passe un dictionnaire contenant le type et le texte du document actuel. 
                #Ces données vont remplir les cases vides {type_document} et {texte_medical} de notre prompt. 
                #notre modèle de langage choisi réfléchit et renvoie sa réponse dans la variable reponse.

                resultat_json = json.loads(reponse.content) #convertit reponse llm (son contenu) en dictionnaire python
                evenements_du_cr = resultat_json.get("evenements", []) #on récupère la liste des événements du compte rendu actuel.

                for idx_ev, ev in enumerate(evenements_du_cr):
                    desc = str(ev.get("description", "")) #on recup description de l'événement parmi la liste des evnmts du cr actuel
                    type_ev = ev.get("type", "")#le type

                    if type_ev not in types_autorises:
                        print(f"Type ignoré : '{type_ev}'") #on filtre les types d'evnmts qui font pas partie de la liste de types autorisés
                        continue

                    champ_a_verifier = (desc + " " + type_ev).upper()
                    if any(mot in champ_a_verifier for mot in mots_interdits):
                        print(f"Événement filtré (mot interdit) : {desc[:60]}") #on filtre les événements contenant des mots interdits dans la description ou le type
                        continue

                    ev["index_priorite"] = types_autorises[type_ev] #on ajoute un champ index_priorite à l'événement --> correspond à la valeur de priorité du type d'événement (ici dictionnaire!)
                    ev["type_cr_parhaf"] = type_cr #on ajoute champ type_cr_parhaf à l'événement --> correspond au type du compte rendu
                    ev["ordre_apparition"] = idx_ev #on ajoute champ ordre_apparition à l'événement --> correspond à l'ordre d'apparition de l'événement dans le compte rendu (utile si dates et index identiques)
                    ev["num_cr_parhaf"] = idx_doc #on ajoute champ num_cr_parhaf à l'événement --> correspond au numéro du compte rendu dans la liste des documents du patient (pr organiser ds ordre chronologique des cr)
                    tous_les_evenements_du_patient.append(ev)
 
            except Exception as e:
                print(f"Erreur sur le document {idx_doc} : {e}")

        break  # patient trouvé, on arrête

    if not patient_trouve:
        print(f"Aucun patient trouvé avec l'id : {id_patient}")

    return tous_les_evenements_du_patient  # on retourne la liste
