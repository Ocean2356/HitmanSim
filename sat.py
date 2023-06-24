import os
import subprocess
from referee.hitman.hitman import HitmanReferee, HC
from itertools import product, combinations

import sys

'''
Codage variables pour GopherSAT:
additioner 21 pour la meme variable appliquee aux cases successives, colonne puis ligne

GN00 = 1
GE00 = 2
GS00 = 3
GO00 = 4
IN00 = 5
IE00 = 6
IS00 = 7
IO00 = 8
T00 = 9
S00 = 10
D00 = 11
W00 = 12
E00 = 13
'''

class Solveur:
    def __init__(self, arbitre):
        self.arbitre = arbitre
        etat_initial = self.arbitre.start_phase1()
        self.infos_carte = {}
        self.m = etat_initial['m'] # nombre de lignes
        self.n = etat_initial['n'] # nombre de colonnes
        self.nb_gardes_total = etat_initial['guard_count']
        self.nb_invites_total = etat_initial['civil_count']
        for i in range(self.m):
            for j in range(self.n):
                self.infos_carte[(j, i)] = None
        offset_range = range(-2, 3)
        self.ecoute_offset = list(product(offset_range, offset_range))
        self.etat_hitman = {
            "etat": etat_initial['status'],
            "position": etat_initial['position'],
            "orientation": etat_initial['orientation'],
            "vision": etat_initial['vision'],
            "nb_voix": etat_initial['hear'],
            "malus": etat_initial['penalties'],
            "est_vu_par_garde": etat_initial['is_in_guard_range']
        }
        self.nb_variables = 13 * self.m * self.n
        self.clauses = self.regles_sat_statiques()
        self.deduire_vue()
        self.etat_hitman['champs_ecoute'] = self.calculer_champs_ecoute()

    def deduire_vue(self):
        for (x, y), content in self.etat_hitman['vision']:
            self.infos_carte[(x, y)] = content
        self.deduire_clauses_unitaires()

    def calculer_champs_ecoute(self):
        champs = []
        for e in self.ecoute_offset:
            new_c = self.etat_hitman['position'][0] + e[0]
            new_l = self.etat_hitman['position'][1] + e[1]
            if new_l >= 0 and new_c >= 0 and new_l < self.m and new_c < self.n:
                champs.append((new_c, new_l))
        return champs

    def peut_avancer(self):
        if ((self.etat_hitman['orientation'] == HC.N and self.etat_hitman['position'][1] == self.m-1)
            or (self.etat_hitman['orientation'] == HC.E and self.etat_hitman['position'][0] == self.n-1)
            or (self.etat_hitman['orientation'] == HC.S and self.etat_hitman['position'][1] == 0)
            or (self.etat_hitman['orientation'] == HC.W and self.etat_hitman['position'][0] == 0)):
            return False
        else:
            return True

    def avancer(self):
        if self.peut_avancer() == True:
            etat_retourne = self.arbitre.move()
            self.etat_hitman['etat'] = etat_retourne['status']
            self.etat_hitman['position'] = etat_retourne['position']
            self.etat_hitman['vision'] = etat_retourne['vision']
            self.etat_hitman['nb_voix'] = etat_retourne['hear']
            self.etat_hitman['malus'] = etat_retourne['penalties']
            self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
            self.deduire_vue()
            self.etat_hitman['champs_ecoute'] = self.calculer_champs_ecoute()
            #self.analyzer_local()
        return self.etat_hitman

    def tourner_horaire(self):
        etat_retourne = self.arbitre.turn_clockwise()
        self.etat_hitman['etat'] = etat_retourne['status']
        self.etat_hitman['orientation'] = etat_retourne['orientation']
        self.etat_hitman['vision'] = etat_retourne['vision']
        self.etat_hitman['malus'] = etat_retourne['penalties']
        self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
        self.deduire_vue()
        #self.analyzer_local()
        return self.etat_hitman

    def tourner_anti_horaire(self):
        etat_retourne = self.arbitre.turn_anti_clockwise()
        self.etat_hitman['etat'] = etat_retourne['status']
        self.etat_hitman['orientation'] = etat_retourne['orientation']
        self.etat_hitman['vision'] = etat_retourne['vision']
        self.etat_hitman['malus'] = etat_retourne['penalties']
        self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
        self.deduire_vue()
        #self.analyzer_local()
        return self.etat_hitman

    def regles_sat_statiques(self):
        liste_regles = []

        for l in range(self.m):
            for c in range(self.n):
                g_n = 1 + 13 * self.n * l + 13 * c
                g_e = 2 + 13 * self.n * l + 13 * c
                g_s = 3 + 13 * self.n * l + 13 * c
                g_o = 4 + 13 * self.n * l + 13 * c
                i_n = 5 + 13 * self.n * l + 13 * c
                i_e = 6 + 13 * self.n * l + 13 * c
                i_s = 7 + 13 * self.n * l + 13 * c
                i_o = 8 + 13 * self.n * l + 13 * c
                t = 9 + 13 * self.n * l + 13 * c
                s = 10 + 13 * self.n * l + 13 * c
                d = 11 + 13 * self.n * l + 13 * c
                w = 12 + 13 * self.n * l + 13 * c
                e = 13 + 13 * self.n * l + 13 * c

                # Une case contient au moins qqchose ou rien
                clause_content = str(g_n) + " " + str(g_e) + " " + str(g_s) + " " + str(g_o) + " "\
                                 + str(i_n) + " " + str(i_e) + " " + str(i_s) + " " + str(i_o) +" "\
                                + str(t) + " " + str(s) + " " + str(d) + " " + str(w) + " " + str(e) + " 0"
                liste_regles.append(clause_content)

                # Une case contient au plus qqchose ou rien
                vars = [g_n, g_e, g_s, g_o, i_n, i_e, i_s, i_o, t, s, d, w, e]
                combinaisons = combinations(vars, 2)
                for c in combinaisons:
                    clause_content_u = "-" + str(c[0]) + " -" + str(c[1]) + " 0"
                    liste_regles.append(clause_content_u)

        # il y a une seule cible
        cible_possible = range(9, 9+13*self.m*self.n, 13)
        clause = ""
        for c in cible_possible:
            clause += str(c) + " "
        clause += "0"
        liste_regles.append(clause)
        combinaisons = combinations(cible_possible, 2)
        for c in combinaisons:
            clause_content_u = "-" + str(c[0]) + " -" + str(c[1]) + " 0"
            liste_regles.append(clause_content_u)

        # il y a une seule corde de piano
        corde_possible = range(10, 10 + 13 * self.m * self.n, 13)
        clause = ""
        for c in corde_possible:
            clause += str(c) + " "
        clause += "0"
        liste_regles.append(clause)
        combinaisons = combinations(corde_possible, 2)
        for c in combinaisons:
            clause_content_u = "-" + str(c[0]) + " -" + str(c[1]) + " 0"
            liste_regles.append(clause_content_u)

        # il y a un seul costume
        costume_possible = range(11, 11 + 13 * self.m * self.n, 13)
        clause = ""
        for c in costume_possible:
            clause += str(c) + " "
        clause += "0"
        liste_regles.append(clause)
        combinaisons = combinations(costume_possible, 2)
        for c in combinaisons:
            clause_content_u = "-" + str(c[0]) + " -" + str(c[1]) + " 0"
            liste_regles.append(clause_content_u)

        return liste_regles

    def analyser_0_voix(self):
        # il n' y a aucune personne non identifiee dans la zone d'ecoute
        zone_a_analyser = {}  # Calcul de la zone a analyser: zones inconnues
        for coord in self.etat_hitman['champs_ecoute']:
            if self.infos_carte[coord] == None:
                zone_a_analyser[coord] = [1, 2, 3, 4, 5, 6, 7, 8]
        variables = []
        for coord in zone_a_analyser.keys():
            c = coord[0]
            l = coord[1]
            for var in zone_a_analyser[coord]:
                variables.append(var + 13 * self.n * l + 13 * c)
        for v in variables:
            clause = "-" + str(v) + " -0"
            if clause not in self.clauses:
                self.clauses.append(clause)

    def analyser_1_voix(self):
        # il y a une personne non identifiee dans la zone d'ecoute
        zone_a_analyser = {} # Calcul de la zone a analyser: zones inconnues
        for coord in self.etat_hitman['champs_ecoute']:
            if self.infos_carte[coord] == None:
                zone_a_analyser[coord] = {HC.GUARD_N: 0, HC.GUARD_E: 0, HC.GUARD_S: 0, HC.GUARD_W: 0,
                                          HC.CIVIL_N: 0, HC.CIVIL_E: 0, HC.CIVIL_S: 0, HC.CIVIL_W: 0}
        variables = []
        # Calcul de toutes les clauses unitaires a tester
        for coord in zone_a_analyser.keys():
            c = coord[0]
            l = coord[1]
            i = 1
            for val in zone_a_analyser[coord].keys():
                zone_a_analyser[coord][val] = i + 13 * self.n * l + 13 * c
                variables.append(i + 13 * self.n * l + 13 * c)
                i += 1
        clause = ""
        for v in variables:
            clause += str(v) + " "
        clause += "0"
        if clause not in self.clauses:
            self.clauses.append(clause)

        # Tester SAT pour chaque clause unitaire: si on montre bottom en ajoutant la negation dans la KB, la clause est vraie
        for coord in zone_a_analyser.keys():
            for val in zone_a_analyser[coord].keys():
                if self.test_gophersat("analyse.cnf", zone_a_analyser[coord][val]) == True:
                    self.infos_carte[coord] = zone_a_analyser[coord][val]
        self.deduire_clauses_unitaires()

    def analyzer_local(self):
        voix_deja_identifiees = 0
        for coord in self.etat_hitman['champs_ecoute']:
            if self.infos_carte[coord] in [HC.GUARD_N, HC.GUARD_E, HC.GUARD_S, HC.GUARD_W, HC.CIVIL_N, HC.CIVIL_E,
                                           HC.CIVIL_S, HC.CIVIL_W]:
                voix_deja_identifiees += 1
        match (self.etat_hitman['nb_voix'] - voix_deja_identifiees):
            case 0:
                self.analyser_0_voix()
            case 1:
                self.analyser_1_voix()

    def deduire_clauses_unitaires(self):
        for coord in self.infos_carte.keys():
            c = coord[0]
            l = coord[1]
            contenu = self.infos_carte[coord]
            if contenu != None:
                var = 0
                match contenu:
                    case HC.EMPTY:
                        var = 13 + 13*self.n*l + 13*c
                    case HC.WALL:
                        var = 12 + 13*self.n*l + 13*c
                    case HC.GUARD_N:
                        var = 1 + 13*self.n*l + 13*c
                    case HC.GUARD_E:
                        var = 2 + 13*self.n*l + 13*c
                    case HC.GUARD_S:
                        var = 3 + 13*self.n*l + 13*c
                    case HC.GUARD_W:
                        var = 4 + 13*self.n*l + 13*c
                    case HC.CIVIL_N:
                        var = 5 + 13*self.n*l + 13*c
                    case HC.CIVIL_E:
                        var = 6 + 13*self.n*l + 13*c
                    case HC.CIVIL_S:
                        var = 7 + 13*self.n*l + 13*c
                    case HC.CIVIL_W:
                        var = 8 + 13*self.n*l + 13*c
                    case HC.PIANO_WIRE:
                        var = 10 + 13*self.n*l + 13*c
                    case HC.SUIT:
                        var = 11 + 13*self.n*l + 13*c
                    case HC.TARGET:
                        var = 9 + 13*self.n*l + 13*c
                clause = str(var) + " 0"
                if clause not in self.clauses:
                    self.clauses.append(clause)

    def test_gophersat(self, nom_fichier, clause_unitaire:int):
        try:
            fichier = open(nom_fichier, "w")
        except:
            print("Echec de l'ouverture du fichier")
        else:
            fichier.write("c " + nom_fichier + "\nc\n")
            fichier.write("p cnf " + str(self.nb_variables) + " " + str(len(self.clauses)) + "\n")
            fichier.write("-" + str(clause_unitaire) + " 0")
            for c in self.clauses:
                fichier.write(c + "\n")
            fichier.close()
            subprocess.run("gophersat --verbose " + nom_fichier + " > resultat.txt", shell=True)
            fichier_dest = open("resultat.txt")
            lignes = fichier_dest.readlines()
            fichier_dest.close()
            for l in lignes:
                if "UNSATISFIABLE" in l:
                    return True
            return False

    def test_gophersat_carte(self, nom_fichier):
        try:
            fichier = open(nom_fichier, "w")
        except:
            print("Echec de l'ouverture du fichier")
        else:
            fichier.write("c " + nom_fichier + "\nc\n")
            fichier.write("p cnf " + str(self.nb_variables) + " " + str(len(self.clauses)) + "\n")
            for c in self.clauses:
                fichier.write(c + "\n")
            fichier.close()
            subprocess.run("gophersat --verbose " + nom_fichier + " > resultat_carte.txt", shell=True)
            fichier_dest = open("resultat_carte.txt")
            lignes = fichier_dest.readlines()
            fichier_dest.close()
            for l in lignes:
                if "SATISFIABLE" in l:
                    return True
            return False
    def fin_phase_1(self):
        for (j, i) in self.infos_carte.keys():
            if self.infos_carte[(j, i)] == None:
                return False
        return True

def main():
    arb = HitmanReferee()
    sv = Solveur(arb)
    print("Nombre de variables: " + str(sv.nb_variables))
    sv.avancer()
    sv.tourner_horaire()
    print(sv.etat_hitman)
    print(sv.infos_carte)
    print(sv.clauses)
    print(sv.test_gophersat_carte("phase1.cnf"))

if __name__ == "__main__":
    path = "/tmp"
    os.chdir(path)
    sys.stdout = open("log.txt", "w")
    main()
