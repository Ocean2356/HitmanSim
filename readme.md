# Projet IA02

## Auteurs : Haiyang MA, Alexandre PAUVAREL

## Fonctionnement du programme

### Phase 1

La phase 1 du projet est composée de plusieurs fichiers : model_phase1, vue_phase1_cmd, ai_phase1 et sat.

Le fichier model_phase1 est responsable de la communication avec l'arbitre et de la gestion de l'état interne de Hitman. La vue_phase1_cmd affiche la carte reconstruite à partir des perceptions de Hitman. L'AI (intelligence artificielle) est chargée de prendre les décisions pour Hitman. Enfin, le fichier sat contient les règles et les variables du problème, contribuant ainsi à la construction du modèle interne.

Dans le fichier model_phase1, nous avons principalement utilisé des dictionnaires pour stocker les perceptions de Hitman, permettant ainsi à l'IA de prendre des décisions éclairées :

- Le dictionnaire knowledge_hear enregistre les voix entendues par Hitman et les associe aux cases correspondantes.
- Le dictionnaire graph est un graphe qui enregistre les états que Hitman a déjà visités.
- La liste frontier contient les états à explorer.
- Le dictionnaire map_info représente la carte reconstruite à partir des perceptions de Hitman.
- La liste garde_seen enregistre les gardes que Hitman a déjà repérés.
- Le dictionnaire penalties enregistre les pénalités que Hitman a déjà subies dans les cases correspondantes.

Chaque état (state) est une structure composée d'une position et d'une orientation.

Dans la partie SAT, nous avons établi les règles génériques de la carte, ainsi que les connaissances nécessaires pour déduire les informations concernant l'écoute de Hitman.

Dans l'IA, nous utilisons une recherche BFS (parcours en largeur) pour déterminer la prochaine case la plus intéressante à visiter parmi celles présentes dans la frontière. Cette décision est prise en utilisant une fonction heuristique qui prend en compte les nouvelles perceptions potentielles de Hitman ainsi que les pénalités qu'il pourrait subir. La phase 1 se termine lorsque la frontière proche est vide, c'est-à-dire qu'il n'y a plus de case à visiter, ou lorsque Hitman a accumulé un nombre de pénalités trop élevé.

### Phase 2

## Forces et faiblesses

### Phase 1

Forces :

- Les fichiers sont bien organisés, ce qui facilite la compréhension, la collaboration et la maintenance.
- Une vue TUI est fournie pour afficher la carte reconstruite à partir des perceptions de Hitman.
- La recherche BFS est efficace pour trouver la prochaine case à visiter.
- Les pondérations des heuristiques sont exposées en tant que paramètres, ce qui permet de les améliorer ultérieurement par méthode machine learning.
- Les tentatives moins prometteuses sont évitées dans la décision IA et la déduction SAT, ce qui permet de réduire le temps de calcul.

Faiblesses :

- Les paramètres de pondération des heuristiques sont déterminés manuellement, ce qui n'est pas optimal.
- La structure du projet n'est pas bien dessinée au début, ce qui a entraîné des fonctions redondantes dans la partie SAT. Mais d'après notre observation, la partie génération de règles SAT et appel de solveur est la plus coûteuse en temps de calcul, donc c'est plus intéressant de combiner les codes rapidement que de les uniformiser.

## Modélisation SAT de la phase 1

### Variables

- Contenu d'une case (x,y):
  - Hitman en case (x,y), orienté Nord: $HN_{xy}$
  - Hitman en case (x,y), orienté Est: $HE_{xy}$
  - Hitman en case (x,y), orienté Sud: $HS_{xy}$
  - Hitman en case (x,y), orienté Ouest: $HO_{xy}$
  - Garde en case (x,y), orienté Nord: $GN_{xy}$
  - Garde en case (x,y), orienté Est: $GE_{xy}$
  - Garde en case (x,y), orienté Sud: $GS_{xy}$
  - Garde en case (x,y), orienté Ouest: $GO_{xy}$
  - Invité en case (x,y), orienté Nord: $IN_{xy}$
  - Invité en case (x,y), orienté Est: $IE_{xy}$
  - Invité en case (x,y), orienté Sud: $IS_{xy}$
  - Invité en case (x,y), orienté Ouest: $IO_{xy}$
  - Cible en case (x,y) : $T_{xy}$ (T pour target)
  - Corde de piano en case (x,y) : $S_{xy}$ (S pour string)
  - Costume de serveur en case (x,y) : $D_{xy}$ (D pour disguise)
  - La case (x,y) est vide : $E_{xy}$ (E pour empty)
  - Mur en case (x,y): $W_{xy}$ (W pour wall)
  - Personne en case (x,y): $P_{xy}$
  - Objet en case (x,y): $O_{xy}$

- Perception de Hitman:
  - Case (x,y) vue par Hitman : $HV_{xy}$
  - Case (x,y) écoutée par Hitman : $HH_{xy}$
  - Nombre de voix entendues par Hitman : $NV_0, NV_1, NV_2, NV_3, NV_4, NV_5$

- Perception des gardes:
  - Case (x,y) vue par garde en (a,b) : $GV_{xy,ab}$

### Règles

- Les gardes et les invités sont des personnes:
  - $GN_{xy}\lor GE_{xy}\lor GS_{xy}\lor GO_{xy}\lor IN_{xy}\lor IE_{xy}\lor IS_{xy}\lor IO_{xy}\lor \vDash P_{xy}$

- Hitman a au moins une orientation:
  - $\vDash HN_{xy}\lor  HE_{xy}\lor  HS_{xy}\lor  HO_{xy}$

- Hitman a une seule orientation:
  - $HN_{xy} <-> ¬HE_{xy} ∧ ¬HS_{xy} ∧ ¬HO_{xy}$
  - $HE_{xy} <-> ¬HN_{xy} ∧ ¬HS_{xy} ∧ ¬HO_{xy}$
  - $HS_{xy} <-> ¬HE_{xy} ∧ ¬HN_{xy} ∧ ¬HO_{xy}$
  - $HO_{xy} <-> ¬HE_{xy} ∧ ¬HS_{xy} ∧ ¬HN_{xy}$

- Le garde a au moins une orientation:
  - $\vDash GN_{xy}\lor  GE_{xy}\lor  GS_{xy}\lor  GO_{xy}$

- Le garde a une seule orientation:
  - $GN_{xy} <-> ¬GE_{xy} ∧ ¬GS_{xy} ∧ ¬GO_{xy}$
  - $GE_{xy} <-> ¬GN_{xy} ∧ ¬GS_{xy} ∧ ¬GO_{xy}$
  - $GS_{xy} <-> ¬GE_{xy} ∧ ¬GN_{xy} ∧ ¬GO_{xy}$
  - $GO_{xy} <-> ¬GE_{xy} ∧ ¬GS_{xy} ∧ ¬GN_{xy}$

- L'invité a au moins une orientation:
  - $\vDash IN_{xy}\lor  IE_{xy}\lor  IS_{xy}\lor  IO_{xy}$

- L'invité a une seule orientation:
  - $IN_{xy} <-> ¬IE_{xy} ∧ ¬IS_{xy} ∧ ¬IO_{xy}$
  - $IE_{xy} <-> ¬IN_{xy} ∧ ¬IS_{xy} ∧ ¬IO_{xy}$
  - $IS_{xy} <-> ¬IE_{xy} ∧ ¬IN_{xy} ∧ ¬IO_{xy}$
  - $IO_{xy} <-> ¬IE_{xy} ∧ ¬IS_{xy} ∧ ¬IN_{xy}$

- Le costume et la corde de piano sont des objets:
  - $D_{xy}\lor S_{xy} \vDash O_{xy}$

- Une case contient soit rien, soit une personne, soit un objet, soit un mur, soit la cible:
  - $\vDash T_{xy}\lor  E_{xy}\lor  P_{xy}\lor  S_{xy}\lor  W_{xy}\lor D_{xy}$

- Une case contient au plus une entité:
  - $P_{xy} <-> ¬D_{xy} ∧ ¬T_{xy} ∧ ¬S_{xy} ∧ ¬E_{xy} ∧ ¬W_{xy}$
  - $T_{xy} <-> ¬S_{xy} ∧ ¬P_{xy} ∧ ¬G_{xy} ∧ ¬D_{xy} ∧ ¬E_{xy}$
  - $D_{xy} <-> ¬T_{xy} ∧ ¬P_{xy} ∧ ¬E_{xy} ∧ ¬W_{xy} ∧ ¬S_{xy}$
  - $S_{xy} <-> ¬T_{xy} ∧ ¬P_{xy} ∧ ¬E_{xy} ∧ ¬W_{xy} ∧ ¬D_{xy}$
  - $E_{xy} <-> ¬T_{xy} ∧ ¬P_{xy} ∧ ¬S_{xy} ∧ ¬W_{xy} ∧ ¬D_{xy}$
  - $W_{xy} <-> ¬T_{xy} ∧ ¬P_{xy} ∧ ¬S_{xy} ∧ ¬E_{xy} ∧ ¬D_{xy}$

- L'unicité et l'existence de Hitman, Cible, Corde de piano et Costume sur la carte :
  - $\alpha_{xy} \vDash \lnot \alpha_{ij}, \quad(i,j)≠(x,y), \quad\alpha=H,C,P,S$
  - $\vDash\alpha_{0,0}\lor\alpha_{0,1}\lor...\lor\alpha_{m,n}, \quad\alpha=H,C,P,S$

- Champs de vision des gardes:
  - $G_{xy} ∧ GN_{xy} -> VG_{xy+1,xy} ∧ VG_{xy+2,xy}$
  - $G_{xy} ∧ GE_{xy} -> VG_{x+1y,xy} ∧ VG_{x+2y,xy}$
  - $G_{xy} ∧ GS_{xy} -> VG_{xy-1,xy} ∧ VG_{xy-2,xy}$
  - $G_{xy} ∧ GO_{xy} -> VG_{x-1y,xy} ∧ VG_{x-2y,xy}$

## Modélisation STRIPS de la phase 2

A représente le contenu d'une case, x et y sont respectivement les abscisses et ordonnées de la case, d est la direction, s est l'etat.
Directions: north -> east -> south -> west (ordre croissant)

### Fluents

At(A, x, y), Direction(A, d), State(A, s)

### État initial

Init(At(Hitman, 0, 0) ∧ At(Empty, 1, 0) ∧ ... ∧ At(Empty, n-1, m-1))

### But

Goal(At(Hitman, 0, 0) ∧ State(Target, dead))

### Actions

Action(Move_up(Hitman, x, y),
PRECOND: At(Hitman, x, y), At(Empty, x, y+1), Direction(Hitman, north)
EFFECT: At(Hitman, x, y+1), ¬At(Hitman, x, y))

Action(Move_right(Hitman, x, y),
PRECOND: At(Hitman, x, y), At(Empty, x+1, y), Direction(Hitman, east)
EFFECT: At(Hitman, x+1, y), ¬At(Hitman, x, y))

Action(Move_down(Hitman, x, y),
PRECOND: At(Hitman, x, y), At(Empty, x, y-1), Direction(Hitman, south)
EFFECT: At(Hitman, x, y-1), ¬At(Hitman, x, y))

Action(Move_left(Hitman, x, y),
PRECOND: At(Hitman, x, y), At(Empty, x-1, y), Direction(Hitman, west)
EFFECT: At(Hitman, x-1, y), ¬At(Hitman, x, y))

Action(Turn_clockwise(Hitman, x, y),
PRECOND: At(Hitman, x, y), Direction(Hitman, d1)
EFFECT: At(Hitman, x, y), Direction(Hitman, d2), ¬At(Hitman, x, d1)) avec d2 > d1 selon l'ordre des orientations défini ci-dessus

Action(Turn_counter_clockwise(Hitman, x, y),
PRECOND: At(Hitman, x, y), Direction(Hitman, d1)
EFFECT: At(Hitman, x, y), Direction(Hitman, d2), ¬At(Hitman, x, d1)) avec d2 < d1 selon l'ordre des orientations défini ci-dessus

Action(Kill_target(x, y),
PRECOND: At(Hitman, x, y), At(Target, x, y), State(String, equipped)
EFFECT: At(Empty, x, y), ¬At(Target, x, y), State(Target, dead))

Action(Neutralize_guard(x, y),
PRECOND: Adjacent(Hitman, x, y), At(Guard, x, y), Direction(Hitman, west)
EFFECT: At(Hitman, x-1, y), ¬At(Hitman, x, y))

Action(Take_costume(x, y),
PRECOND: At(Hitman, x, y), At(Disguise, x, y),
EFFECT: ¬At(Disguise, x, y), At(Empty, x, y), State(Disguise, acquired))

Action(Put_on_costume,
PRECOND: State(Disguise, acquired),
EFFECT: State(Disguise, put_on))

Action(Take_weapon(x, y),
PRECOND: At(Hitman, x, y), At(String, x, y),
EFFECT: ¬At(String, x, y), At(Empty, x, y), State(String, acquired))

## Programmation Python phase 2

Algorithme de parcours utilisé: A*
