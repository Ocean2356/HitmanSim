# Projet IA02

Haiyang MA, Alexandre PAUVAREL

## 1. Modélisation SAT de la phase 1

Détails à représenter:

- Champ de vision des gardes et des civils
- Capacité d'écoute de Hitman

### Variables

- Contenu d'une case (x,y) :
  - Hitman : $H_{xy}$
  - Garde : $G_{xy}$
  - Civil : $C_{xy}$
  - Cible : $D_{xy}$ (D pour Dhalek)
  - Corde de piano : $P_{xy}$
  - Costume de serveur : $S_{xy}$
  - Vide : $V_{xy}$
  - Mur : $M_{xy}$

- Phase 1
  - Percepts de Hitman :
    - Inconnu : $I_{xy}$
    - Vision instantané : $Vision_{xy}$
    - Écoute instantané : $Ecoute_{xy}$
    - Nombre de voix entendue : $NV_0, NV_1, NV_2, NV_3, NV_4, NV_5$

  - Action de Hitman :
    - Tourner horaire : $T_{H}$
    - Tourner anti-horaire : $T_{A}$
    - Avancer : $A$

### Règles

- L'unicité et l'existence de contenu d'une case (x,y):
  - $\alpha_{xy} \vDash\lnot \beta_{xy}, \quad \alpha,\beta=H,G,C,D,P,S,V,M,\quad \alpha ≠ \beta$
  - $\vDash\alpha_{xy}\lor \beta_{xy}\lor  \gamma_{xy}\lor  \delta_{xy}\lor  \epsilon_{xy}\lor  \zeta_{xy}\lor  \eta_{xy}\lor  \theta_{xy}, \quad \alpha,\beta,\gamma,\delta,\epsilon,\zeta,\eta,\theta=H,G,C,D,P,S,V,M$

- L'unicité et l'existence de Hitman, Cible, Corde de piano et Costume sur la carte :
  - $\alpha_{xy} \vDash \lnot \alpha_{ij}, \quad(i,j)≠(x,y), \quad\alpha=H,C,P,S$
  - $\vDash\alpha_{0,0}\lor\alpha_{0,1}\lor...\lor\alpha_{m,n}, \quad\alpha=H,C,P,S$

- L'unicité et l'existence d'action de Hitman :
  - $\alpha\vDash\lnot\beta,\quad\alpha,\beta=T_{H},T_{A},A$
  - $\vDash T_{H}\lor T_{A}\lor A$

## 2. Programmation Python phase 1

transmettre les perceptions de Hitman à la connaissance de la carte
sauvegarder la base de connaissance dans python

- Remarque :
  - Hitman est invisible pour les gardes quand il est dans la même case qu'un invité

## 3. Modélisation STRIPS de la phase 2

## 4. Programmation Python phase 2

## 5. Rapport

- Modélisation
- Forces et faiblesse de programmes
