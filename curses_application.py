from hitman.hitman.hitman import HitmanReferee, HC
from sat import Solveur
import curses
import time


class Application:
    def __init__(self, solveur:Solveur):
        self.solveur = solveur
        self.etat = self.solveur.etat_hitman  # etat, position, orientation, vision, nb_voix, malus, est_vu_par_garde
        self.carte = self.solveur.infos_carte
        self.m = self.solveur.m
        print("nb lignes: ", self.m)
        self.n = self.solveur.n
        print("nb colonnes: ", self.n)
        self.nb_gardes_total = self.solveur.nb_gardes_total
        self.nb_invites_total = self.solveur.nb_invites_total

        self.scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.scr.keypad(True)
        self.mise_en_page()
        self.lancer_application()

    def mise_en_page(self):
        # Diviser l'écran en deux fenêtres verticales
        hauteur, largeur = self.scr.getmaxyx()
        hauteur_carte = self.m

        self.fenetre_carte = self.scr.subwin(hauteur_carte+2, largeur, 0, 0)
        self.fenetre_chaines = self.scr.subwin(hauteur - hauteur_carte, largeur, hauteur_carte, 0)

        self.afficher_carte()
        self.afficher_etat()

    def afficher_carte(self):
        # Calculer la position du coin supérieur gauche de la grille
        debut_ligne = self.m
        debut_colonne = 0

        # Parcourir chaque cellule de la grille et l'afficher à l'écran
        for i in range(self.m):
            for j in range(self.n):
                # Calculer la position de chaque cellule dans la fenêtre
                x = debut_colonne + 4*j
                y = debut_ligne - i

                # Afficher la valeur de la cellule à l'écran
                if (j, i) == self.etat['position']:
                    match self.etat['orientation']:
                        case HC.N: self.fenetre_carte.addstr(y, x, str("HN"))
                        case HC.E: self.fenetre_carte.addstr(y, x, str("HE"))
                        case HC.S: self.fenetre_carte.addstr(y, x, str("HS"))
                        case HC.W: self.fenetre_carte.addstr(y, x, str("HO"))
                    continue

                match self.carte[(j,i)]:
                    case HC.GUARD_N:
                        self.fenetre_carte.addstr(y, x, str("GN"))
                    case HC.GUARD_E:
                        self.fenetre_carte.addstr(y, x, str("GE"))
                    case HC.GUARD_S:
                        self.fenetre_carte.addstr(y, x, str("GS"))
                    case HC.GUARD_W:
                        self.fenetre_carte.addstr(y, x, str("GO"))
                    case HC.CIVIL_N:
                        self.fenetre_carte.addstr(y, x, str("IN"))
                    case HC.CIVIL_E:
                        self.fenetre_carte.addstr(y, x, str("IE"))
                    case HC.CIVIL_S:
                        self.fenetre_carte.addstr(y, x, str("IS"))
                    case HC.CIVIL_W:
                        self.fenetre_carte.addstr(y, x, str("IO"))
                    case HC.EMPTY:
                        self.fenetre_carte.addstr(y, x, str("E "))
                    case HC.WALL:
                        self.fenetre_carte.addstr(y, x, str("W "))
                    case HC.SUIT:
                        self.fenetre_carte.addstr(y, x, str("D "))
                    case HC.PIANO_WIRE:
                        self.fenetre_carte.addstr(y, x, str("S "))
                    case HC.TARGET:
                        self.fenetre_carte.addstr(y, x, str("T "))
                    case None:
                        self.fenetre_carte.addstr(y, x, str("? "))
        self.fenetre_carte.refresh()

    def afficher_etat(self):
        self.fenetre_chaines.addstr(1, 1, "Nombre de voix: " + str(self.etat['nb_voix']))
        self.fenetre_chaines.addstr(2, 1, "Vu par garde: " + str(self.etat['est_vu_par_garde']))
        self.fenetre_chaines.addstr(3, 1, "Malus: " + str(self.etat['malus']))
        self.fenetre_chaines.refresh()

    def tourner_sens_horaire(self):
        self.etat = self.solveur.tourner_horaire()
        self.mettre_a_jour_carte()
        self.mettre_a_jour_etat()

    def tourner_sens_antihoraire(self):
        self.etat = self.solveur.tourner_anti_horaire()
        self.mettre_a_jour_carte()
        self.mettre_a_jour_etat()

    def avancer(self):
        self.etat = self.solveur.avancer()
        self.mettre_a_jour_carte()
        self.mettre_a_jour_etat()

    def mettre_a_jour_carte(self):
        self.carte = self.solveur.infos_carte
        self.afficher_carte()

    def mettre_a_jour_etat(self):
        self.etat = self.solveur.etat_hitman
        self.afficher_etat()

    def lancer_application(self):
        try:
            curses.cbreak()
            while self.solveur.fin_phase_1() == False:
                key = self.scr.getch()
                if key == 119: # W
                    self.avancer()
                elif key == 97: # A
                    self.tourner_sens_antihoraire()
                elif key == 100: # D
                    self.tourner_sens_horaire()
                elif key == 113:
                    break
                time.sleep(0.03)
        except KeyboardInterrupt:
            curses.nocbreak()

def main(stdscr):
    arbitre = HitmanReferee()
    solveur = Solveur(arbitre)
    app = Application(solveur)

    while True:
        # Effacer l'écran
        #app.scr.clear()

        # Récupérer la saisie de l'utilisateur
        c = stdscr.getch()

        # Gérer la saisie de l'utilisateur (exemple : quitter avec la touche 'q')
        if c == ord('q'):
            break


if __name__ == '__main__':
    curses.wrapper(main)