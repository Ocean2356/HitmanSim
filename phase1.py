from enum import Enum

from phase1 import Orientation, TypePersonne

class TypePersonne(Enum):
    Garde = 1
    Invite = 2
    Cible = 3
    Hitman = 4

class TypeObjet(Enum):
    Corde = 1
    Costume = 2

class AutreType(Enum):
    Vide = 1
    Mur = 2

class Orientation(Enum):
    Nord = 1
    Est = 2
    Sud = 3
    Ouest = 4

# Represente ce qu'une case peut contenir
class ContenuCase:
    def __init__(self, transparence:bool) -> None:
        self.transparent = transparence

# Pour les personnes
class Personne(ContenuCase):
    def __init__(self, type: TypePersonne, transparence:bool, orientation: Orientation, champsVision: int) -> None:
        super().__init__(transparence)
        self.type = type
        self.orientation = orientation
        self.champsVision = champsVision

# Pour la corde et le costume
class Objet(ContenuCase):
    def __init__(self, type: TypeObjet) -> None:
        super().__init__(False)
        self.type = type

# Pour les murs et les cases vides
class AutreTypeCase(ContenuCase):
    def __init__(self, transparence: bool, type: AutreType) -> None:
        super().__init__(transparence)
        self.type = type

# Represente une case
class Case:
    def __init__(self, contenu:ContenuCase, x: int, y: int) -> None:
        self.contenu = contenu
        self.x = x
        self.y = y

# Represente Hitman
class Hitman(Personne):
    def __init__(self, orientation: Orientation, champsEcoute:list, position:Case) -> None:
        super().__init__(Hitman, False, orientation, 3)
        self.champsEcoute = champsEcoute
        self.position = position
        
    def avancer(nouvelleCase: Case):
        position = nouvelleCase
    

    





class Hitman:
    def __init__(self, p:tuple(int, int)) -> None:
        self.position = p
        self.vision = 

    Content = Enum('Content',['g','c','d','p','s','v','m'])
    # Content = Enum('g','c','d','p','s','v','m')
    Genre = Enum('Genre', ['Person','Object','Place'])

    def at_least_one(vars:list[int]) -> list[int]:
        return vars

    def unique(vars:list[int]) -> list[list[int]]:
        cnf = []
        # cnf.append(vars)
        for i in range(len(vars)-1):
            for j in range(i+1, len(vars)):
                cnf.append([-vars[i], -vars[j]])
        return cnf

    def percept2knowledge(self, p:tuple(int,int), o:tuple(int,int), n:int, d:int, t:Content) -> list[list[int]]:
        knowledge = []
        for i in range(1,d):
            # knowledge.append([p[0]+i*o[0], p[1]+i*o[1], self.Content.v])
            knowledge.append([p+i*o, self.Content.v])
        # knowledge.append([p[0]+d*o[0], p[1]+d*o[1], t])
        knowledge.append([p+d*o, t])





class Salle:
    def __init__(self, m: int, n: int, nbI: int, nbG: int):
        self.m = m
        self.n = n
        self.nbI = nbI
        self.nbG = nbG

class Reperage:
    def __init__(self, salle: Salle):
        self.contenue = [[None for i in range(salle.m)] for j in range(salle.n)]

def termine(r: Reperage) -> bool:
    pass

def nextCase(h: Hitman, k: Knowledge) -> Case:
    pass

def goToCase(h: Hitman, c: Case) -> list[Action]:
    pass

def updateHitman(h: Hitman, a: list[Action]) -> Hitman:
    pass

def percept(h: Hitman) -> Perception:
    pass

def updateKnowledge(k: Knowledge, p: Perception) -> Knowledge:
    pass

def updateReperage(r: Reperage, k: Knowledge) -> Reperage:
    pass

def reperer(s: Salle, h: Hitman) -> Reperage:
    while(not termine(reperage)):
        c = nextCase(h, reperage)
        a = goToCase(h, c)
        h = updateHitman(h, a)
        p = percept(h)
        k = updateKnowledge(k, p)
        reperage = updateReperage(reperage, k)
    return reperage