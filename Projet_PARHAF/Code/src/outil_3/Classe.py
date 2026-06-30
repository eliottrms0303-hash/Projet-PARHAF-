from __future__ import annotations
from dataclasses import asdict, dataclass



#---------------------------------------------------------------------
#-------- Classe contenant les attributs définissant un document ------
#---------------------------------------------------------------------


@dataclass(slots=True)
class CaracteristiquesDocument:
    #------ Métadonnées générales ------
    ID : str #
    specialty : str #F
    pool : str #F

    #------ Infos sur le scénario ------
    name : str #E
    age : float #N
    sex : str #F
    admission_mode : str | None #F
    discharge_mode : str | None #F
    type_of_care : str | None #E

    #------ Infos sur le document ------
    Type : list[str] #F
    header : list[str] #E
    text : list[str] #E

    #------ Infos sur l'abstract ------
    primary_procedure : list[str] | None #E
    primary_diagnosis : list[str] #E
    length_of_stay : float #N

    #------ Vecteur -------
    vecteur : dict[str, list[float]]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
        
