from referee.hitman.hitman import *

demo_map = {
    (0,0): HC.EMPTY,
    (1,0): HC.EMPTY,
    (2,0): HC.WALL,
    (3,0): HC.WALL,
    (4,0): HC.EMPTY,
    (5,0): HC.PIANO_WIRE,
    (6,0): HC.EMPTY,
    (0,1): HC.EMPTY,
    (1,1): HC.EMPTY,
    (2,1): HC.EMPTY,
    (3,1): HC.EMPTY,
    (4,1): HC.EMPTY,
    (5,1): HC.EMPTY,
    (6,1): HC.EMPTY,
    (0,2): HC.WALL,
    (1,2): HC.WALL,
    (2,2): HC.EMPTY,
    (3,2): HC.GUARD_E,
    (4,2): HC.EMPTY,
    (5,2): HC.CIVIL_W,
    (6,2): HC.CIVIL_E,
    (0,3): HC.TARGET,
    (1,3): HC.WALL,
    (2,3): HC.EMPTY,
    (3,3): HC.EMPTY,
    (4,3): HC.EMPTY,
    (5,3): HC.CIVIL_N,
    (6,3): HC.EMPTY,
    (0,4): HC.EMPTY,
    (1,4): HC.WALL,
    (2,4): HC.EMPTY,
    (3,4): HC.EMPTY,
    (4,4): HC.EMPTY,
    (5,4): HC.EMPTY,
    (6,4): HC.EMPTY,
    (0,5): HC.EMPTY,
    (1,5): HC.EMPTY,
    (2,5): HC.EMPTY,
    (3,5): HC.SUIT,
    (4,5): HC.GUARD_S,
    (5,5): HC.WALL,
    (6,5): HC.WALL
}

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
        if noeud['heuristique'] < open_list[i]['heuristique']:
            open_list.insert(i, noeud)
            return
    open_list.append(noeud)

def reconstituer_chemin(closed_list):
    print("reconstitution...")
    chemin = [closed_list[-1]]
    noeud_courant = chemin[0]
    #print("noeud depart:", noeud_courant)
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

class AI2():
    def __init__(self, arbitre, infos_map):
        self.carte = infos_map
        self.arbitre = arbitre
        etat_initial = self.arbitre.start_phase2()
        self.etat_hitman = {
            "etat": etat_initial['status'],
            "position": etat_initial['position'],
            "orientation": etat_initial['orientation'],
            "vision": etat_initial['vision'],
            "nb_voix": etat_initial['hear'],
            "malus": etat_initial['penalties'],
            "est_vu_par_garde": etat_initial['is_in_guard_range'],
            "est-vu_par_invite": etat_initial['is_in_civil_range'],
            "a_costume": etat_initial['has_suit'],
            "porte_costume": etat_initial['is_suit_on'],
            "a_corde": etat_initial['has_weapon'],
            "cible_tuee": etat_initial['is_target_down']
        }
        self.m = etat_initial['m']
        self.n = etat_initial['n']

    def peut_avancer(self):
        x, y = self.etat_hitman['position']
        if ((self.etat_hitman['orientation'] == HC.N and self.etat_hitman['position'][1] == self.m - 1)
                or (self.etat_hitman['orientation'] == HC.E and self.etat_hitman['position'][0] == self.n - 1)
                or (self.etat_hitman['orientation'] == HC.S and self.etat_hitman['position'][1] == 0)
                or (self.etat_hitman['orientation'] == HC.W and self.etat_hitman['position'][0] == 0)
                or (self.etat_hitman['orientation'] == HC.N and self.carte[(x, y + 1)] in [HC.GUARD_N, HC.GUARD_S,
                                                                                                 HC.GUARD_E,
                                                                                                 HC.GUARD_W])
                or (self.etat_hitman['orientation'] == HC.E and self.carte[(x + 1, y)] in [HC.GUARD_N, HC.GUARD_S,
                                                                                                 HC.GUARD_E,
                                                                                                 HC.GUARD_W])
                or (self.etat_hitman['orientation'] == HC.S and self.carte[(x, y - 1)] in [HC.GUARD_N, HC.GUARD_S,
                                                                                                 HC.GUARD_E,
                                                                                                 HC.GUARD_W])
                or (self.etat_hitman['orientation'] == HC.W and self.carte[(x - 1, y)] in [HC.GUARD_N, HC.GUARD_S,
                                                                                                 HC.GUARD_E,
                                                                                                 HC.GUARD_W])):
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
            self.etat_hitman['est_vu_par_invite'] = etat_retourne['is_in_civil_range']
            self.etat_hitman['a_costume'] = etat_retourne['has_suit']
            self.etat_hitman['porte_costume'] = etat_retourne['is_suit_on']
            self.etat_hitman['a_corde'] = etat_retourne['has_weapon']
            self.etat_hitman['cible_tuee'] = etat_retourne['is_target_down']
        return self.etat_hitman

    def tourner_horaire(self):
        etat_retourne = self.arbitre.turn_clockwise()
        self.etat_hitman['etat'] = etat_retourne['status']
        self.etat_hitman['orientation'] = etat_retourne['orientation']
        self.etat_hitman['vision'] = etat_retourne['vision']
        self.etat_hitman['malus'] = etat_retourne['penalties']
        self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
        self.etat_hitman['est_vu_par_invite'] = etat_retourne['is_in_civil_range']
        self.etat_hitman['a_costume'] = etat_retourne['has_suit']
        self.etat_hitman['porte_costume'] = etat_retourne['is_suit_on']
        self.etat_hitman['a_corde'] = etat_retourne['has_weapon']
        self.etat_hitman['cible_tuee'] = etat_retourne['is_target_down']
        return self.etat_hitman

    def tourner_anti_horaire(self):
        etat_retourne = self.arbitre.turn_anti_clockwise()
        self.etat_hitman['etat'] = etat_retourne['status']
        self.etat_hitman['orientation'] = etat_retourne['orientation']
        self.etat_hitman['vision'] = etat_retourne['vision']
        self.etat_hitman['malus'] = etat_retourne['penalties']
        self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
        self.etat_hitman['est_vu_par_invite'] = etat_retourne['is_in_civil_range']
        self.etat_hitman['a_costume'] = etat_retourne['has_suit']
        self.etat_hitman['porte_costume'] = etat_retourne['is_suit_on']
        self.etat_hitman['a_corde'] = etat_retourne['has_weapon']
        self.etat_hitman['cible_tuee'] = etat_retourne['is_target_down']
        return self.etat_hitman

    def tuer_cible(self):
        if self.carte[self.etat_hitman['position']] == HC.TARGET:
            etat_retourne = self.arbitre.kill_target()
            self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
            self.etat_hitman['est_vu_par_invite'] = etat_retourne['is_in_civil_range']
            self.etat_hitman['a_costume'] = etat_retourne['has_suit']
            self.etat_hitman['porte_costume'] = etat_retourne['is_suit_on']
            self.etat_hitman['a_corde'] = etat_retourne['has_weapon']
            self.etat_hitman['cible_tuee'] = etat_retourne['is_target_down']
            self.etat_hitman['malus'] = etat_retourne['penalties']
            self.carte[self.etat_hitman['position']] = HC.EMPTY
        return self.etat_hitman

    def neutraliser_garde(self, position):
        if self.carte[self.etat_hitman[position]] in [HC.GUARD_N, HC.GUARD_E, HC.GUARD_S, HC.GUARD_W]:
            etat_retourne = self.arbitre.neutralize_guard()
            self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
            self.etat_hitman['est_vu_par_invite'] = etat_retourne['is_in_civil_range']
            self.etat_hitman['malus'] = etat_retourne['penalties']
            self.carte[self.etat_hitman['position']] = HC.EMPTY
        return self.etat_hitman

    def neutraliser_invite(self, position):
        if self.carte[self.etat_hitman[position]] in [HC.CIVIL_N, HC.CIVIL_E, HC.CIVIL_S, HC.CIVIL_W]:
            etat_retourne = self.arbitre.neutralize_civil()
            self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
            self.etat_hitman['est_vu_par_invite'] = etat_retourne['is_in_civil_range']
            self.etat_hitman['malus'] = etat_retourne['penalties']
            self.carte[self.etat_hitman['position']] = HC.EMPTY
        return self.etat_hitman

    def prendre_costume(self):
        if self.carte[self.etat_hitman['position']] == HC.SUIT:
            etat_retourne = self.arbitre.take_suit()
            self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
            self.etat_hitman['est_vu_par_invite'] = etat_retourne['is_in_civil_range']
            self.etat_hitman['a_costume'] = etat_retourne['has_suit']
            self.etat_hitman['malus'] = etat_retourne['penalties']
            self.carte[self.etat_hitman['position']] = HC.EMPTY
        return self.etat_hitman

    def enfiler_costume(self):
        if self.etat_hitman['a_costume'] == True:
            etat_retourne = self.arbitre.put_on_suit()
            self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
            self.etat_hitman['est_vu_par_invite'] = etat_retourne['is_in_civil_range']
            self.etat_hitman['porte_costume'] = etat_retourne['is_suit_on']
            self.etat_hitman['malus'] = etat_retourne['penalties']
        return self.etat_hitman

    def prendre_corde(self):
        if self.carte[self.etat_hitman['position']] == HC.PIANO_WIRE:
            etat_retourne = self.arbitre.take_weapon()
            self.etat_hitman['est_vu_par_garde'] = etat_retourne['is_in_guard_range']
            self.etat_hitman['est_vu_par_invite'] = etat_retourne['is_in_civil_range']
            self.etat_hitman['a_corde'] = etat_retourne['has_weapon']
            self.etat_hitman['malus'] = etat_retourne['penalties']
            self.carte[self.etat_hitman['position']] = HC.EMPTY
        return self.etat_hitman

    def trouver_position(self, objet):
        for k in self.carte.keys():
            if self.carte[k] == objet:
                return k

    def est_vu_par_garde(self, position):
        x = position[0]
        y = position[1]
        gardes_meme_colonne = []
        gardes_meme_ligne = []
        for x1,y1 in self.carte.keys():
            if x1 == x and self.carte[(x1,y1)] in [HC.GUARD_N, HC.GUARD_S]:
                gardes_meme_colonne.append((x1,y1))
            elif y1 == y and self.carte[(x1,y1)] in [HC.GUARD_W, HC.GUARD_E]:
                gardes_meme_ligne.append((x1,y1))
        for g in gardes_meme_colonne:
            distance = distance_manhattan(position, g)
            if ((self.carte[g] == HC.GUARD_N and y > g[1] and distance <= 2)
            or (self.carte[g] == HC.GUARD_S and y < g[1] and distance <= 2)):
                return True
        for g in gardes_meme_ligne:
            distance = distance_manhattan(position, g)
            if ((self.carte[g] == HC.GUARD_E and x > g[0] and distance <= 2)
                    or (self.carte[g] == HC.GUARD_W and x < g[0] and distance <= 2)):
                return True
        return False

    def est_vu_par_invite(self, position):
        x = position[0]
        y = position[1]
        invites_meme_colonne = []
        invites_meme_ligne = []
        for x1, y1 in self.carte.keys():
            if x1 == x and self.carte[(x1, y1)] in [HC.CIVIL_N, HC.CIVIL_S]:
                invites_meme_colonne.append((x1, y1))
            elif y1 == y and self.carte[(x1, y1)] in [HC.CIVIL_E, HC.CIVIL_W]:
                invites_meme_ligne.append((x1, y1))
        for g in invites_meme_colonne:
            distance = distance_manhattan(position, g)
            if ((self.carte[g] == HC.CIVIL_N and y > g[1] and distance <= 2)
                    or (self.carte[g] == HC.CIVIL_S and y < g[1] and distance <= 2)):
                return True
        for g in invites_meme_ligne:
            distance = distance_manhattan(position, g)
            if ((self.carte[g] == HC.CIVIL_E and x > g[0] and distance <= 2)
                    or (self.carte[g] == HC.CIVIL_W and x < g[0] and distance <= 2)):
                return True
        return False

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
            if self.carte[noeud_avancer['position']] not in [HC.WALL, HC.GUARD_E, HC.GUARD_S, HC.GUARD_N, HC.GUARD_W]:
                if self.est_vu_par_garde(noeud_avancer['position']) == True:
                    noeud_avancer['cout'] += 5
                else:
                    noeud_avancer['cout'] += 1
                liste_voisins.append(noeud_avancer)
        liste_voisins.append(noeud_tourner_horaire)
        liste_voisins.append(noeud_tourner_antihoraire)
        # L'heuristique n'est pas mise à jour pour la case avancer, le faire dans A*
        return liste_voisins

    def a_etoile_phase2(self, noeud_depart, case_arrivee):
        # print("test a*")
        print("depart: ", noeud_depart)
        print("arrivee: ", case_arrivee)
        open_list = [noeud_depart]
        closed_list = []
        while len(open_list) != 0:
            # print("open list: ")
            # for i in open_list:
            #     print(i['position'], i['orientation'], i['heuristique'])
            u = open_list[0]
            open_list.pop(0)
            closed_list.append(u)
            if u['position'] == case_arrivee:
                # print("Closed list:", closed_list)
                return reconstituer_chemin(closed_list)
            voisins = self.voisins(u)
            # print("Case: ", u['orientation'], u['position'])
            # print("Voisins: ")
            # for v in voisins:
            #     print(v['position'], v['orientation'])
            # print("Nombre voisins:", len(voisins))
            nb_ajouts = 0
            for v in voisins:
                # print(type(open_list))
                v['heuristique'] = v['cout'] + distance_manhattan(v['position'], case_arrivee)
                if (existe_dans_closed_list(v, closed_list) == False and existe_dans_open_list_avec_cout_inferieur(v, open_list) == False):
                    inserer_open_list(open_list, v)
                    nb_ajouts += 1
            # print("Nb d'ajouts: ", nb_ajouts)
        print("Fail")
        return []

    def executer_phase2(self):
        # Etape 1: trouver costume
        print("trouver costume")
        noeud_courant = {'parent': None, 'position': self.etat_hitman['position'],
                         'orientation': self.etat_hitman['orientation'],
                         'cout': 0}
        case_costume = self.trouver_position(HC.SUIT)
        noeud_courant['heuristique'] = distance_manhattan(noeud_courant['position'], case_costume)

        chemin_costume = self.a_etoile_phase2(noeud_courant, case_costume)
        for noeud in chemin_costume[1:]:
            if 'action' in noeud.keys():
                if noeud['action'] == 'avancer':
                    self.avancer()
                elif noeud['action'] == 'tourner_horaire':
                    self.tourner_horaire()
                else:
                    self.tourner_anti_horaire()
        self.prendre_costume()
        self.enfiler_costume()

        # Etape 2: trouver corde de piano
        print("trouver corde")
        noeud_courant = {'parent': None, 'position': self.etat_hitman['position'],
                         'orientation': self.etat_hitman['orientation'],
                         'cout': 0}
        case_corde = self.trouver_position(HC.PIANO_WIRE)
        noeud_courant['heuristique'] = distance_manhattan(noeud_courant['position'], case_corde)

        chemin_corde = self.a_etoile_phase2(noeud_courant, case_corde)
        for noeud in chemin_corde[1:]:
            if 'action' in noeud.keys():
                if noeud['action'] == 'avancer':
                    self.avancer()
                elif noeud['action'] == 'tourner_horaire':
                    self.tourner_horaire()
                else:
                    self.tourner_anti_horaire()
        self.prendre_corde()

        # Etape 3: tuer cible
        print("tuer cible")
        noeud_courant = {'parent': None, 'position': self.etat_hitman['position'],
                         'orientation': self.etat_hitman['orientation'],
                         'cout': 0}
        case_cible = self.trouver_position(HC.TARGET)
        noeud_courant['heuristique'] = distance_manhattan(noeud_courant['position'], case_cible)

        chemin_cible = self.a_etoile_phase2(noeud_courant, case_cible)
        for noeud in chemin_cible[1:]:
            if 'action' in noeud.keys():
                if noeud['action'] == 'avancer':
                    self.avancer()
                elif noeud['action'] == 'tourner_horaire':
                    self.tourner_horaire()
                else:
                    self.tourner_anti_horaire()
        self.tuer_cible()

        # Etape 4: retour case depart
        print("retour case depart")
        noeud_courant = {'parent': None, 'position': self.etat_hitman['position'],
                         'orientation': self.etat_hitman['orientation'],
                         'cout': 0}
        noeud_courant['heuristique'] = distance_manhattan(noeud_courant['position'], (0, 0))

        chemin_retour = self.a_etoile_phase2(noeud_courant, (0,0))
        for noeud in chemin_retour[1:]:
            if 'action' in noeud.keys():
                if noeud['action'] == 'avancer':
                    self.avancer()
                elif noeud['action'] == 'tourner_horaire':
                    self.tourner_horaire()
                else:
                    self.tourner_anti_horaire()
        if self.etat_hitman['position'] == (0, 0):
            print("fin mission")

    def resultat_phase2(self):
        return self.arbitre.end_phase2()

def main():
    arbitre = HitmanReferee()
    ai = AI2(arbitre, demo_map)
    '''
    noeud_test = {'parent': None, 'position': ai.etat_hitman['position'],
                     'orientation': ai.etat_hitman['orientation'],
                     'cout': 0}
    case_but = ai.trouver_position(HC.TARGET)
    noeud_test['heuristique'] = distance_manhattan(noeud_test['position'], case_but)
    c1 = ai.a_etoile_phase2(noeud_test, case_but)
    print(c1)
    for noeud in c1[1:]:
        if 'action' in noeud.keys():
            if noeud['action'] == 'avancer':
                ai.avancer()
                print('avance')
            elif noeud['action'] == 'tourner_horaire':
                ai.tourner_horaire()
                print('tourner_horaire')
            else:
                ai.tourner_anti_horaire()
                print('tourner_anti_horaire')
    '''
    ai.executer_phase2()
    print(ai.etat_hitman)
    print(ai.resultat_phase2())


if __name__ == "__main__":
    main()
