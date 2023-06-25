import referee.hitman.hitman as hm
from itertools import product, combinations
from typing import Dict, Tuple, List
from enum import Enum
import subprocess


class HC(Enum):
    UNKNOWN = -1
    NOT_PERSON = 0
    PERSON = 18
    
    # NOT_FRONTIER = 0
    # FRONTIER = 1


class State():
    def __init__(self, position, orientation):
        self.position = position
        self.orientation = hm.HC(orientation)

    def __eq__(self, other):
        return self.position == other.position and self.orientation == other.orientation
    
    def __hash__(self):
        return hash((self.position, self.orientation))
    
    # def __format__(self):
    #     return "({}, {})".format(self.position, self.orientation)

    def __str__(self):
        return "({}, {})".format(self.position, self.orientation)

    def __repr__(self):
        return "({}, {})".format(self.position, self.orientation)


class Model1():
    def __init__(self, hr):
        self.hr = hr
        self.status = self.hr.start_phase1()
        self.state = State(self.status['position'], self.status['orientation'])
        self.gain = 0
        self.previous_penalties = 0
        self.n = self.status['n']
        self.m = self.status['m']

        self.knowledge_hear = {}
        self.graph = {}
        self.frontier = [self.state]
        self.map_info = {}
        self.garde_seen = {}
        self.penalties = {}

        self.listening_dist = 2
        self.vision_dist = 3
        possible_offset = range(-self.listening_dist, self.listening_dist + 1)
        self.offsets_listening: List[Tuple(int, int)] = list(product(possible_offset, possible_offset))
        self.offsets_neighbour: List[Tuple(int, int)] = [(-1,0), (1,0), (0,-1), (0,1)]

        self.offsets_orientation = {
            hm.HC.N: (0, 1),
            hm.HC.E: (1, 0),
            hm.HC.S: (0, -1),
            hm.HC.W: (-1, 0),
            hm.HC.GUARD_N: (0, 1),
            hm.HC.GUARD_E: (1, 0),
            hm.HC.GUARD_S: (0, -1),
            hm.HC.GUARD_W: (-1, 0),
            hm.HC.CIVIL_N: (0, 1),
            hm.HC.CIVIL_E: (1, 0),
            hm.HC.CIVIL_S: (0, -1),
            hm.HC.CIVIL_W: (-1, 0),
        } 

        self.Moveable = {
            hm.HC.EMPTY,
            hm.HC.CIVIL_N,
            hm.HC.CIVIL_E,
            hm.HC.CIVIL_S,
            hm.HC.CIVIL_W,
            hm.HC.TARGET,
            hm.HC.SUIT,
            hm.HC.PIANO_WIRE,
        }

        self.Person = {
            hm.HC.GUARD_N,
            hm.HC.GUARD_E,
            hm.HC.GUARD_S,
            hm.HC.GUARD_W,
            hm.HC.CIVIL_N,
            hm.HC.CIVIL_E,
            hm.HC.CIVIL_S,
            hm.HC.CIVIL_W,
        }

        self.Garde = {
            hm.HC.GUARD_N,
            hm.HC.GUARD_E,
            hm.HC.GUARD_S,
            hm.HC.GUARD_W,
        }
        
        self.Unseen = {
            HC.UNKNOWN,
            HC.NOT_PERSON,
            HC.PERSON,
        }

        for i in range(self.n):
            for j in range(self.m):
                self.knowledge_hear[(i, j)] = HC.UNKNOWN
                # self.frontier[(i, j)] = HC.NOT_FRONTIER
                self.map_info[(i, j)] = HC.UNKNOWN
                self.penalties[(i, j)] = 0
        self.map_info[(0, 0)] = hm.HC.EMPTY
        self.clauses = self.regles_sat_statiques()
        self.nb_variables = 13 * self.m * self.n
        self.analyse_movement()
        
    def do_movement(self, movement: str):
        match movement[0]:
            case "w": self.status = self.hr.move()
            case "a": self.status = self.hr.turn_anti_clockwise()
            case "d": self.status = self.hr.turn_clockwise()
            # case "s": self.do_send()
            case _: self.status['status'] = "Unknown movement, please enter w, a, or d"
        self.analyse_movement()
        self.deduire_clauses_unitaires()

    def calculate_hear_range(self):
        champs = []
        for e in self.offsets_listening:
            new_c = self.state.position[0] + e[0]
            new_l = self.state.position[1] + e[1]
            if new_l >= 0 and new_c >= 0 and new_l < self.m and new_c < self.n:
                champs.append((new_c, new_l))
        return champs

    # def move(self):
    #     self.status = self.hr.move()
    # def turn_anti_clockwise(self):
    #     self.status = self.hr.turn_anti_clockwise()
    # def turn_clockwise(self):
    #     self.status = self.hr.turn_clockwise()

    def do_send(self):
        map_info = self.map_info
        for (x, y), content in map_info.items():
            if content == HC.UNKNOWN:
                map_info[(x, y)] = hm.HC.EMPTY
            elif content == HC.NOT_PERSON:
                map_info[(x, y)] = hm.HC.EMPTY
            elif content == HC.PERSON:
                map_info[(x, y)] = hm.HC.GUARD_N
        all_correct = self.hr.send_content(self.map_info)
        print("Sending content...")
        print("All correct: {}".format(all_correct))
        _, score, hist, map_content = self.hr.end_phase1()
        print("Score: {}".format(score))
        print("History: {}".format(hist))
        # print("Map content: {}".format(map_content))
        return all_correct, score, hist, map_content

    def analyse_movement(self):
        if self.status['status'] != "OK":
            print(self.status['status'])
            return

        if self.status['vision'] and self.status['vision'][-1][1] != hm.HC.EMPTY and self.map_info[self.status['vision'][-1][0]] in self.Unseen:
            self.gain += 2
            if self.status['vision'][-1][1] in self.Garde:
                self.garde_seen[self.status['vision'][-1][0]] = self.status['vision'][-1][1]
        
        for (x, y), content in self.status['vision']:
            self.map_info[(x, y)] = content

        self.knowledge_hear[self.status['position']] = self.status['hear']

        self.analyze_local()
        self.deduire_clauses_unitaires()
        self.update_graph()

    def analyze_local(self):
        voix_deja_identifiees = 0
        for coord in self.calculate_hear_range():
            if self.map_info[coord] in [hm.HC.GUARD_N, hm.HC.GUARD_E, hm.HC.GUARD_S, hm.HC.GUARD_W, hm.HC.CIVIL_N, hm.HC.CIVIL_E,
                                           hm.HC.CIVIL_S, hm.HC.CIVIL_W]:
                voix_deja_identifiees += 1
        match (self.knowledge_hear[self.state.position] - voix_deja_identifiees):
            case 0:
                self.analyze_0_voice()
            case 1:
                self.analyze_1_voice()

    def analyze_0_voice(self):
        # il n' y a aucune personne non identifiee dans la zone d'ecoute
        zone_a_analyser = {}  # Calcul de la zone a analyser: zones inconnues
        for coord in self.calculate_hear_range():
            if self.map_info[coord] == None:
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

    def analyze_1_voice(self):
        # il y a une personne non identifiee dans la zone d'ecoute
        zone_a_analyser = {} # Calcul de la zone a analyser: zones inconnues
        for coord in self.calculate_hear_range():
            if self.map_info[coord] == HC.UNKNOWN:
                zone_a_analyser[coord] = {hm.HC.GUARD_N: 0, hm.HC.GUARD_E: 0, hm.HC.GUARD_S: 0, hm.HC.GUARD_W: 0,
                                          hm.HC.CIVIL_N: 0, hm.HC.CIVIL_E: 0, hm.HC.CIVIL_S: 0, hm.HC.CIVIL_W: 0}
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
                if self.test_gophersat("analyse.cnf", zone_a_analyser[coord][val]) == False:
                    self.map_info[coord] = val
                    break
        self.deduire_clauses_unitaires()

    def deduce_listening(self, position: Tuple[int, int]):
        if self.knowledge_hear[position] == HC.UNKNOWN:
            return []
        count, zone = self.get_listening(position)
        if count < 5 :
            if count == self.knowledge_hear[position]:
                for i, j in zone:
                    if self.map_info[(i, j)] == HC.UNKNOWN:
                        self.map_info[(i, j)] = HC.NOT_PERSON

            caseUnknown = 0
            for i, j in zone:
                if self.map_info[(i, j)] == HC.UNKNOWN:
                    caseUnknown += 1
            if caseUnknown == self.knowledge_hear[position] - count:
                for i, j in zone:
                    if self.map_info[(i, j)] == HC.UNKNOWN:
                        self.map_info[(i, j)] = HC.PERSON
        return 

    def get_listening(self, position: Tuple[int, int]) -> Tuple[int, List]:
        count = 0
        x, y = position
        zone = []
        for i, j in self.offsets_listening:
            pos_x, pos_y = x + i, y + j
            if pos_x >= self.status['n'] or pos_y >= self.status['m'] or pos_x < 0 or pos_y < 0:
                continue
            zone.append((pos_x, pos_y))
            if self.map_info[(pos_x, pos_y)] in self.Person:
                count += 1
            if count == 5:
                break
        return count, zone

    def left(self, state: State) -> State:
        o = hm.HC(state.orientation)
        return State(state.position, (o.value - hm.HC.N.value + 3) % 4 + hm.HC.N.value)
    def right(self, state: State) -> State:
        o = hm.HC(state.orientation)
        return State(state.position, (o.value - hm.HC.N.value + 1) % 4 + hm.HC.N.value)
    def forward(self, state: State) -> State:
        x0, y0 = state.position
        o = hm.HC(state.orientation)
        x, y = self.offsets_orientation[o]
        return State((x0+x, y0+y), state.orientation)
        
    def moveable(self, state: State) -> bool:
        if state.position not in self.map_info:
            return False
        if self.map_info[state.position] not in self.Moveable:
            return False
        
        return True

    def update_frontier(self, state):
        self.frontier.remove(state)
        for i in self.graph[state]:
            if i not in self.graph:
                self.frontier.append(i)

    def update_gain(self):
        self.penalties[self.status['position']] = -(self.status['penalties'] - self.previous_penalties)
        self.gain += self.penalties[self.status['position']]
        self.previous_penalties = self.status['penalties']
        # print(self.penalties)

    def update_graph(self):
        self.state = State(self.status['position'], self.status['orientation'])
        
        if self.state in self.graph:
            return

        self.graph[self.state] = []
        self.graph[self.state].append(self.left(self.state))
        self.graph[self.state].append(self.right(self.state))
        tmp = self.forward(self.state)
        if self.moveable(tmp):
            self.graph[self.state].append(tmp)
        self.update_frontier(self.state)
        self.update_gain()

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

    def deduire_clauses_unitaires(self):
        for coord in self.map_info.keys():
            c = coord[0]
            l = coord[1]
            contenu = self.map_info[coord]
            if contenu != None:
                var = 0
                match contenu:
                    case hm.HC.EMPTY:
                        var = 13 + 13*self.n*l + 13*c
                    case hm.HC.WALL:
                        var = 12 + 13*self.n*l + 13*c
                    case hm.HC.GUARD_N:
                        var = 1 + 13*self.n*l + 13*c
                    case hm.HC.GUARD_E:
                        var = 2 + 13*self.n*l + 13*c
                    case hm.HC.GUARD_S:
                        var = 3 + 13*self.n*l + 13*c
                    case hm.HC.GUARD_W:
                        var = 4 + 13*self.n*l + 13*c
                    case hm.HC.CIVIL_N:
                        var = 5 + 13*self.n*l + 13*c
                    case hm.HC.CIVIL_E:
                        var = 6 + 13*self.n*l + 13*c
                    case hm.HC.CIVIL_S:
                        var = 7 + 13*self.n*l + 13*c
                    case hm.HC.CIVIL_W:
                        var = 8 + 13*self.n*l + 13*c
                    case hm.HC.PIANO_WIRE:
                        var = 10 + 13*self.n*l + 13*c
                    case hm.HC.SUIT:
                        var = 11 + 13*self.n*l + 13*c
                    case hm.HC.TARGET:
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
