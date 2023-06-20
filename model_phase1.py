import referee.hitman.hitman as hm
from itertools import product
from typing import Dict, Tuple, List
from enum import Enum


class HC(Enum):
    UNKNOWN = -1
    NOT_PERSON = 0
    PERSON = 18
    
    NOT_FRONTIER = 0
    FRONTIER = 1


class State():
    def __init__(self, position, orientation):
        self.position = position
        self.orientation = orientation

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


class Model():
    def __init__(self):
        self.hr = hm.HitmanReferee()
        self.status = self.hr.start_phase1()
        self.n = self.status['n']
        self.m = self.status['m']
        self.knowledge_hear = {}
        self.graph = {}
        self.frontier = [State(self.status['position'], self.status['orientation'])]
        self.map_info = {}
        self.listening_dist = 2
        possible_offset = range(-self.listening_dist, self.listening_dist + 1)
        self.offsets_listening: List[Tuple(int, int)] = list(product(possible_offset, possible_offset))
        self.offsets_neighbour: List[Tuple(int, int)] = [(-1,0), (1,0), (0,-1), (0,1)]
        self.offsets_orientation = {
            hm.HC.N: (0, 1),
            hm.HC.E: (1, 0),
            hm.HC.S: (0, -1),
            hm.HC.W: (-1, 0),
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
        for i in range(self.n):
            for j in range(self.m):
                self.knowledge_hear[(i, j)] = HC.UNKNOWN
                # self.frontier[(i, j)] = HC.NOT_FRONTIER
                self.map_info[(i, j)] = HC.UNKNOWN
        self.analyse_movement()
        self.map_info[(0, 0)] = hm.HC.EMPTY
        
    def do_movement(self, movement: str):
        match movement[0]:
            case "w": self.status = self.hr.move()
            case "a": self.status = self.hr.turn_anti_clockwise()
            case "d": self.status = self.hr.turn_clockwise()
            case _: self.status['status'] = "Unknown movement, please enter w, a, or d"
        self.analyse_movement()

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
        print("Map content: {}".format(map_content))

    def analyse_movement(self):
        if self.status['status'] == "OK":
            self.knowledge_hear[self.status['position']] = self.status['hear']
            for (x, y), content in self.status['vision']:
                if self.map_info[(x, y)] == HC.UNKNOWN:
                    self.map_info[(x, y)] = content
            self.deduce_listening(self.status['position'])
            if self.status['vision'] and self.status['vision'][-1][1] in self.Person:
                pos_x, pos_y = self.status['vision'][-1][0]
                for i, j in self.offsets_listening:
                    position = (pos_x + i, pos_y + j)
                    if position in self.map_info:
                        self.deduce_listening(position)
            self.update_graph()
        else:
            print(self.status['status'])

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
            if self.map_info[(pos_x, pos_y)] in [
                hm.HC.CIVIL_N,
                hm.HC.CIVIL_E,
                hm.HC.CIVIL_S,
                hm.HC.CIVIL_W,
                hm.HC.GUARD_N,
                hm.HC.GUARD_E,
                hm.HC.GUARD_S,
                hm.HC.GUARD_W,
            ]:
                count += 1
            if count == 5:
                break
        return count, zone

    def left(self, state: State) -> State:
        return State(state.position, (state.orientation.value - hm.HC.N.value + 1) % 4 + hm.HC.N.value)
    def right(self, state: State) -> State:
        return State(state.position, (state.orientation.value - hm.HC.N.value + 3) % 4 + hm.HC.N.value)
    def forward(self, state: State) -> State:
        x0, y0 = state.position
        x, y = self.offsets_orientation[state.orientation]
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

    def update_graph(self):
        state = State(self.status['position'], self.status['orientation'])
        
        if state in self.graph:
            return

        self.graph[state] = []
        self.graph[state].append(self.left(state))
        self.graph[state].append(self.right(state))
        tmp = self.forward(state)
        if self.moveable(tmp):
            self.graph[state].append(tmp)
        self.update_frontier(state)
