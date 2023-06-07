import referee.hitman.hitman as hm
from itertools import product
from typing import Dict, Tuple, List
from enum import Enum
import cmd


class HC(Enum):
    UNKNOWN = -1
    NOT_PERSON = 0
    PERSON = 18
    
    NOT_FRONTIER = 0
    FRONTIER = 1


class HitmanDemo(cmd.Cmd):
    # intro = 'Welcome to the hitman demo.\nType help or ? to list commands.\n'
    prompt = '\n(Hitman) '

    def __init__(self):
        super().__init__()
        self.hr = hm.HitmanReferee()
        self.status = self.hr.start_phase1()
        self.knowledge_hear = {}
        self.frontier = []
        self.map_info = {}
        self.listening_dist = 2
        possible_offset = range(-self.listening_dist, self.listening_dist + 1)
        self.offsets_listening: List[Tuple(int, int)] = list(product(possible_offset, possible_offset))
        self.offsets_neighbour: List[Tuple(int, int)] = [(-1,0), (1,0), (0,-1), (0,1)]
        for i in range(self.status['n']):
            for j in range(self.status['m']):
                self.knowledge_hear[(i, j)] = HC.UNKNOWN
                # self.frontier[(i, j)] = HC.NOT_FRONTIER
                self.map_info[(i, j)] = HC.UNKNOWN
        

    def preloop(self) -> None:
        print("Welcome to the hitman demo.")
        print("Type help or ? to list commands.")
        print("Starting game...")
        print("Map size: {}*{}".format(self.status['n'], self.status['m']))
        print("Guards: ", self.status['guard_count'])
        print("Civilians: ", self.status['civil_count'])
        self.analyse_movement()
        return super().preloop()


    def do_movement(self, movement: str):
        match movement[0]:
            case "w": self.status = self.hr.move()
            case "a": self.status = self.hr.turn_anti_clockwise()
            case "d": self.status = self.hr.turn_clockwise()
            case _: self.status['status'] = "Unknown movement, please enter w, a, or d"
        self.analyse_movement()
    def do_w(self, inp):
        self.do_movement("w")
    def do_a(self, inp):
        self.do_movement("a")
    def do_d(self, inp):
        self.do_movement("d")

    def help_movement(self):
        print("Move forward: w")
        print("Turn anti-clockwise: a")
        print("Turn clockwise: d")
    # def help_w(self):
    #     print("Move forward")
    # def help_a(self):
    #     print("Turn anti-clockwise")
    # def help_d(self):
    #     print("Turn clockwise")


    def do_send(self):
        map_info = self.map_info
        for (x, y), content in map_info.items():
            if content == HC.UNKNOWN:
                map_info[(x, y)] = hm.HC.EMPTY
            elif content == HC.NOT_PERSON:
                map_info[(x, y)] = hm.HC.EMPTY
            elif content == HC.PERSON:
                map_info[(x, y)] = hm.HC.GUARD_N
        observed = self.hr.send_content(self.map_info)
        print("Sending content...")
        print("Observed: {}".format(observed))
        _, score, hist, map_content = self.hr.end_phase1()
        print("Score: {}".format(score))
        print("History: {}".format(hist))
        print("Map content: {}".format(map_content))
    def do_s(self, inp):
        self.do_send()
    
    def help_send(self):
        print("Send content to referee")
    # def help_s(self):
    #     print("Send content to referee")


    def do_quit(self, inp):
        print("Quitting...")
        return True
    def do_q(self, inp):
        return self.do_quit(inp)

    def help_quit(self):
        print("Quit the game")


    def analyse_movement(self):
        if self.status['status'] == "OK":
            new_known = []
            self.knowledge_hear[self.status['position']] = self.status['hear']
            for (x, y), content in self.status['vision']:
                if self.map_info[(x, y)] == HC.UNKNOWN:
                    new_known.append((x, y))
                    self.map_info[(x, y)] = content
            if self.status['vision'] and self.status['vision'][-1][1] in [
                hm.HC.CIVIL_N,
                hm.HC.CIVIL_E,
                hm.HC.CIVIL_S,
                hm.HC.CIVIL_W,
                hm.HC.GUARD_N,
                hm.HC.GUARD_E,
                hm.HC.GUARD_S,
                hm.HC.GUARD_W,
            ]:
                pos_x, pos_y = self.status['vision'][-1][0]
                for i, j in self.offsets_listening:
                    position = (pos_x + i, pos_y + j)
                    if position in self.map_info:
                        new_known += self.deduce_listening(position)

            new_known += self.deduce_listening(self.status['position'])
            self.update_frontier(new_known)
            print("New known: {}".format(new_known))
            print("Frontier: {}".format(self.frontier))
            self.print_map()
            self.print_status()
        else:
            print(self.status['status'])


    def deduce_listening(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        if self.knowledge_hear[position] == HC.UNKNOWN:
            return []
        # print("Deduce listening at {}".format(position))
        count, zone = self.get_listening(position)
        new_known = []
        if count < 5 :
            if count == self.knowledge_hear[position]:
                for i, j in zone:
                    if self.map_info[(i, j)] == HC.UNKNOWN:
                        self.map_info[(i, j)] = HC.NOT_PERSON
                        new_known.append((i, j))

            caseUnknown = 0
            for i, j in zone:
                if self.map_info[(i, j)] == HC.UNKNOWN:
                    caseUnknown += 1
            if caseUnknown == self.knowledge_hear[position] - count:
                for i, j in zone:
                    if self.map_info[(i, j)] == HC.UNKNOWN:
                        self.map_info[(i, j)] = HC.PERSON
                        new_known.append((i, j))
        return new_known


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


    def update_frontier(self, new_known: List[Tuple[int, int]]):
        frontier_tmp = []
        for (x, y) in new_known:
            for i, j in self.offsets_neighbour:
                pos_x, pos_y = x + i, y + j
                if pos_x >= self.status['n'] or pos_y >= self.status['m'] or pos_x < 0 or pos_y < 0:
                    continue
                if self.map_info[(pos_x, pos_y)] == HC.UNKNOWN:
                    frontier_tmp.append((pos_x, pos_y))
        for (x, y) in self.frontier:
            if self.map_info[(x, y)] != HC.UNKNOWN:
                self.frontier.remove((x, y))
        for (x, y) in frontier_tmp:
            if self.map_info[(x, y)] != HC.UNKNOWN:
                continue
            self.frontier.append((x, y))


    def print_status(self):
        print("Position: ", self.status['position'])
        print("Orientation: ", self.status['orientation'])
        print("Vision: ", self.status['vision'])
        print("Hear: ", self.status['hear'])
        print("Penalties: ", self.status['penalties'])
        print("Is in guard range: ", self.status['is_in_guard_range'])


    def print_map(self):
        # the map is turned 90 degrees clockwise
        for x in range(self.status['n']):
            for y in range(self.status['m']):
                if (x, y) == self.status['position']:
                    match self.status['orientation']:
                        case hm.HC.N: print(">", end="")
                        case hm.HC.E: print("v", end="")
                        case hm.HC.S: print("<", end="")
                        case hm.HC.W: print("^", end="")
                    continue
                content = self.map_info[(x, y)]
                match content:
                    case hm.HC.EMPTY: print(" ", end="")
                    case hm.HC.WALL: print("#", end="")
                    case hm.HC.GUARD_N: print("N", end="")
                    case hm.HC.GUARD_E: print("E", end="")
                    case hm.HC.GUARD_S: print("S", end="")
                    case hm.HC.GUARD_W: print("W", end="")
                    case hm.HC.CIVIL_N: print("n", end="")
                    case hm.HC.CIVIL_E: print("e", end="")
                    case hm.HC.CIVIL_S: print("s", end="")
                    case hm.HC.CIVIL_W: print("w", end="")
                    case hm.HC.TARGET: print("!", end="")
                    case hm.HC.SUIT: print("%", end="")
                    case hm.HC.PIANO_WIRE: print("~", end="")
                    case HC.NOT_PERSON: print(".", end="")
                    case HC.PERSON: print("&", end="")
                    case _: print("?", end="")
            print()


if __name__ == "__main__":
    HitmanDemo().cmdloop()
