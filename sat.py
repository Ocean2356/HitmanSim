import subprocess
from referee.hitman.hitman import HitmanReferee, HC
from itertools import product, combinations


def distance_manhattan(position1, position2):
    return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])

def noeuds_egaux(noeud1, noeud2):
    if (noeud1['position'] == noeud2['position'] and noeud1['orientation'] == noeud2['orientation']
    and noeud1['cout'] == noeud2['cout'] and noeud1['heuristique'] == noeud2['heuristique']):
        return True
    else:
        return False

def existe_dans_closed_list(noeud, c_list):
    for e in c_list:
        if noeud['position'] == e['position'] and noeud['orientation'] == e['orientation']:
            return True
    return False

def existe_dans_open_list_avec_cout_inferieur(noeud, o_list):
    #if type(o_list) == <NoneType>
    if len(o_list) == 0:
        return False
    for e in o_list:
        if noeud['position'] == e['position'] and noeud['orientation'] == e['orientation'] and noeud['cout'] > e['cout']:
            return True
    return False

def inserer_open_list(open_list, noeud):
    if len(open_list) == 0:
        open_list.append(noeud)
        return
    for i in range(len(open_list)):
        if (noeud['heuristique'] < open_list[i]['heuristique'] or
                (noeud['heuristique'] == open_list[i]['heuristique'] and noeud['heuristique'] - noeud['cout'] < open_list[i]['heuristique'] - open_list[i]['cout'])):
            open_list.insert(i, noeud)
            return
    open_list.append(noeud)

def reconstituer_chemin(closed_list):
    chemin = [closed_list[-1]]
    noeud_courant = chemin[0]
    while noeud_courant['parent'] != None:
        noeud_courant = noeud_courant['parent']
        chemin.insert(0, noeud_courant)
    return chemin

def get_sequence_actions(chemin):
    liste = []
    for n in chemin:
        if 'action' in n.keys():
            liste.append(n['action'])
    return liste

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

class SolveurPhase1:
    def __init__(self, arbitre):
        self.arbitre = arbitre
        etat_initial = self.arbitre.start_phase1()
        self.infos_carte = {}
        self.m = etat_initial['m'] # nombre de lignes
        self.n = etat_initial['n'] # nombre de colonnes
        self.nb_gardes_total = etat_initial['guard_count']
        self.nb_invites_total = etat_initial['civil_count']
        self.nb_gardes_restant = self.nb_gardes_total
        self.nb_invites_restant = self.nb_invites_total
        self.costume_trouve = False
        self.cible_trouvee = False
        self.corde_trouvee = False
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
        self.infos_carte[self.etat_hitman['position']] = HC.EMPTY
        self.nb_variables = 13 * self.m * self.n
        self.clauses = self.regles_sat_statiques()
        self.deduire_vue()
        self.etat_hitman['champs_ecoute'] = self.calculer_champs_ecoute()
        self.score_phase1 = 0

    def deduire_vue(self):
        for (x, y), contenu in self.etat_hitman['vision']:
            if contenu == HC.TARGET:
                self.cible_trouvee = True
            elif contenu == HC.PIANO_WIRE:
                self.corde_trouvee = True
            elif contenu == HC.SUIT:
                self.costume_trouve = True
            elif contenu in [HC.GUARD_N, HC.GUARD_E, HC.GUARD_S, HC.GUARD_W] and self.infos_carte[(x,y)] == None:
                self.nb_gardes_restant -= 1
            elif contenu in [HC.CIVIL_N, HC.CIVIL_E, HC.CIVIL_S, HC.CIVIL_W] and self.infos_carte[(x,y)] == None:
                self.nb_invites_restant -= 1
            self.infos_carte[(x, y)] = contenu
        self.deduire_clauses_unitaires()

    def get_champs_vision(self):
        liste = []
        x,y = self.etat_hitman['position']
        match self.etat_hitman['orientation']:
            case HC.N:
                if self.infos_carte[(x,y+1)] == HC.EMPTY:
                    liste.append((x,y+1))
                    liste.append((x,y+2))
                else:
                    liste.append((x, y + 1))
            case HC.E:
                if self.infos_carte[(x+1, y)] == HC.EMPTY:
                    liste.append((x+1, y ))
                    liste.append((x+2, y ))
                else:
                    liste.append((x+1, y))
            case HC.S:
                if self.infos_carte[(x, y -1)] == HC.EMPTY:
                    liste.append((x, y - 1))
                    liste.append((x, y - 2))
                else:
                    liste.append((x, y - 1))
            case HC.W:
                if self.infos_carte[(x-1, y)] == HC.EMPTY:
                    liste.append((x-1, y ))
                    liste.append((x-1, y))
                else:
                    liste.append((x-1, y ))
        return liste

    def calculer_champs_ecoute(self):
        champs = []
        for e in self.ecoute_offset:
            new_c = self.etat_hitman['position'][0] + e[0]
            new_l = self.etat_hitman['position'][1] + e[1]
            if new_l >= 0 and new_c >= 0 and new_l < self.m and new_c < self.n:
                champs.append((new_c, new_l))
        return champs

    def peut_avancer(self):
        x,y = self.etat_hitman['position']
        if ((self.etat_hitman['orientation'] == HC.N and self.etat_hitman['position'][1] == self.m-1)
            or (self.etat_hitman['orientation'] == HC.E and self.etat_hitman['position'][0] == self.n-1)
            or (self.etat_hitman['orientation'] == HC.S and self.etat_hitman['position'][1] == 0)
            or (self.etat_hitman['orientation'] == HC.W and self.etat_hitman['position'][0] == 0)
        or (self.etat_hitman['orientation'] == HC.N and self.infos_carte[(x,y+1)] in [HC.GUARD_N, HC.GUARD_S, HC.GUARD_E, HC.GUARD_W])
        or (self.etat_hitman['orientation'] == HC.E and self.infos_carte[(x+1,y)] in [HC.GUARD_N, HC.GUARD_S, HC.GUARD_E, HC.GUARD_W])
        or (self.etat_hitman['orientation'] == HC.S and self.infos_carte[(x,y-1)] in [HC.GUARD_N, HC.GUARD_S, HC.GUARD_E, HC.GUARD_W])
        or (self.etat_hitman['orientation'] == HC.W and self.infos_carte[(x-1,y)] in [HC.GUARD_N, HC.GUARD_S, HC.GUARD_E, HC.GUARD_W])):
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
            self.analyzer_local()
        return self.etat_hitman

    def tourner_horaire(self):
        etat_retourne = self.arbitre.turn_clockwise()
        self.etat_hitman['etat'] = etat_retourne['status']
        self.etat_hitman['orientation'] = etat_retourne['orientation']
        self.etat_hitman['vision'] = etat_retourne['vision']
        self.etat_hitman['malus'] = etat_retourne['penalties']
        self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
        self.deduire_vue()
        self.analyzer_local()
        return self.etat_hitman

    def tourner_anti_horaire(self):
        etat_retourne = self.arbitre.turn_anti_clockwise()
        self.etat_hitman['etat'] = etat_retourne['status']
        self.etat_hitman['orientation'] = etat_retourne['orientation']
        self.etat_hitman['vision'] = etat_retourne['vision']
        self.etat_hitman['malus'] = etat_retourne['penalties']
        self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
        self.deduire_vue()
        self.analyzer_local()
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
                    if val in [HC.GUARD_N, HC.GUARD_E, HC.GUARD_S, HC.GUARD_W] and self.infos_carte[coord] == None:
                        self.nb_gardes_restant -= 1
                    elif val in [HC.CIVIL_N, HC.CIVIL_E, HC.CIVIL_S, HC.CIVIL_W] and self.infos_carte[coord] == None:
                        self.nb_invites_restant -= 1
                    self.infos_carte[coord] = val
                    break
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

    # condition d'arret: nb civils, nb gardes, cible, corde, costume
    def fin_phase_1(self):
        for c in self.infos_carte.keys():
            if self.infos_carte[c] == None:
                return False
        return True

    def est_vu_par_garde(self, position):
        x = position[0]
        y = position[1]
        gardes_meme_colonne = []
        gardes_meme_ligne = []
        for x1,y1 in self.infos_carte.keys():
            if x1 == x and self.infos_carte[(x1,y1)] in [HC.GUARD_N, HC.GUARD_S]:
                gardes_meme_colonne.append((x1,y1))
            elif y1 == y and self.infos_carte[(x1,y1)] in [HC.GUARD_W, HC.GUARD_E]:
                gardes_meme_ligne.append((x1,y1))
        for g in gardes_meme_colonne:
            distance = distance_manhattan(position, g)
            if ((self.infos_carte[g] == HC.GUARD_N and y > g[1] and distance <= 2)
            or (self.infos_carte[g] == HC.GUARD_S and y < g[1] and distance <= 2)):
                return True
        for g in gardes_meme_colonne:
            distance = distance_manhattan(position, g)
            if ((self.infos_carte[g] == HC.GUARD_E and x > g[0] and distance <= 2)
                    or (self.infos_carte[g] == HC.GUARD_W and x < g[0] and distance <= 2)):
                return True
        return False

    def case_inconnue_plus_proche(self, position):
        cases_vides = []
        for p in self.infos_carte.keys():
            if (self.infos_carte[p] == None):
                cases_vides.append(p)
        resultat = cases_vides[0]
        for c in cases_vides:
            if distance_manhattan(position, c) < distance_manhattan(position, resultat):
                resultat = c
        return resultat

    # un noeud est represente par un dictionnaire avec les champs: noeud_parent, action, position, orientation, cout, heuristique

    def voisins(self, noeud_courant):
        liste_voisins = []
        position_courante = noeud_courant['position']
        orientation_courante = noeud_courant['orientation']
        cout_courant = noeud_courant['cout']
        noeud_avancer = {}
        noeud_tourner_horaire = {}
        noeud_tourner_antihoraire = {}
        match noeud_courant['orientation']:
            case HC.N:
                noeud_avancer = {"position": (position_courante[0], position_courante[1]+1), "orientation": HC.N, "cout": cout_courant}
                noeud_tourner_horaire = {"position": position_courante, "orientation": HC.E, "cout": cout_courant + 1}
                noeud_tourner_antihoraire = {"position": position_courante, "orientation": HC.W, "cout": cout_courant + 1}
            case HC.E:
                noeud_avancer = {"position": (position_courante[0]+1, position_courante[1]), "orientation": HC.E, "cout": cout_courant}
                noeud_tourner_horaire = {"position": position_courante, "orientation": HC.S, "cout": cout_courant + 1}
                noeud_tourner_antihoraire = {"position": position_courante, "orientation": HC.N, "cout": cout_courant + 1}
            case HC.S:
                noeud_avancer = {"position": (position_courante[0], position_courante[1] - 1), "orientation": HC.S, "cout": cout_courant}
                noeud_tourner_horaire = {"position": position_courante, "orientation": HC.W, "cout": cout_courant + 1}
                noeud_tourner_antihoraire = {"position": position_courante, "orientation": HC.E, "cout": cout_courant + 1}
            case HC.W:
                noeud_avancer = {"position": (position_courante[0]-1, position_courante[1]), "orientation": HC.W, "cout": cout_courant}
                noeud_tourner_horaire = {"position": position_courante, "orientation": HC.N, "cout": cout_courant + 1}
                noeud_tourner_antihoraire = {"position": position_courante, "orientation": HC.S, "cout": cout_courant + 1}
        noeud_avancer["action"] = "avancer"
        noeud_avancer["parent"] = noeud_courant
        noeud_tourner_horaire["action"] = "tourner_horaire"
        noeud_tourner_horaire["parent"] = noeud_courant
        noeud_tourner_antihoraire["action"] = "tourner_antihoraire"
        noeud_tourner_antihoraire["parent"] = noeud_courant
        if (noeud_avancer['position'][0] in range(0, self.n)
        and noeud_avancer['position'][1] in range(0, self.m)):
            if self.infos_carte[noeud_avancer['position']] not in [HC.WALL, HC.GUARD_E, HC.GUARD_S, HC.GUARD_N, HC.GUARD_W]:
                if self.est_vu_par_garde(noeud_avancer['position']) == True:
                    noeud_avancer['cout'] += 5
                else:
                    noeud_avancer['cout'] += 1
                liste_voisins.append(noeud_avancer)
        liste_voisins.append(noeud_tourner_horaire)
        liste_voisins.append(noeud_tourner_antihoraire)
        # L'heuristique n'est pas mise à jour pour la case avancer, le faire dans A*
        return liste_voisins

    def executer_phase_1(self):
        noeud_courant = {'parent': None, 'position': self.etat_hitman['position'], 'orientation': self.etat_hitman['orientation'],
                         'cout': 0}
        noeud_courant['heuristique'] = distance_manhattan(noeud_courant['position'], self.case_inconnue_plus_proche(noeud_courant['position']))
        while self.fin_phase_1() == False:
            for k in self.infos_carte.keys():
                noeud_courant = {'parent': None, 'position': self.etat_hitman['position'], 'orientation': self.etat_hitman['orientation'], 'cout': 0}
                if self.infos_carte[k] == None:
                    case_suivante = k
                    noeud_courant['heuristique'] = distance_manhattan(noeud_courant['position'], k)
                    chemin_suivant = self.a_etoile_phase1(noeud_courant, case_suivante)
                    for noeud in chemin_suivant[1:]:
                        if 'action' in noeud.keys():
                            if noeud['action'] == 'avancer':
                                self.avancer()
                            elif noeud['action'] == 'tourner_horaire':
                                self.tourner_horaire()
                            else:
                                self.tourner_anti_horaire()
                if self.fin_phase_1() == True:
                    break

        return self.etat_hitman['malus']


    def a_etoile_phase1(self, noeud_depart, case_arrivee):
        open_list = [noeud_depart]
        closed_list = []
        while len(open_list) != 0:
            u = open_list[0]
            open_list.pop(0)
            closed_list.append(u)
            if u['position'] == case_arrivee:
                return reconstituer_chemin(closed_list)
            voisins = self.voisins(u)
            for v in voisins:
                v['heuristique'] = v['cout'] + distance_manhattan(v['position'], case_arrivee)
                if (existe_dans_closed_list(v, closed_list) == False and existe_dans_open_list_avec_cout_inferieur(v, open_list) == False):
                    inserer_open_list(open_list, v)

        return []

    def get_carte(self):
        return self.infos_carte


def main():
    arb = HitmanReferee()
    sv = SolveurPhase1(arb)

    print(sv.etat_hitman)
    sv.executer_phase_1()

    for c in sv.infos_carte.keys():
        print(c, ": ", sv.infos_carte[c])
    print(sv.etat_hitman['malus'])

if __name__ == "__main__":
    main()
