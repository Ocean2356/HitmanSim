import referee.hitman.hitman as hm
from itertools import product
from typing import Dict, Tuple
import cmd

class HitmanDemo(cmd.Cmd):
    # intro = 'Welcome to the hitman demo.\nType help or ? to list commands.\n'
    prompt = '\n(Hitman) '

    def __init__(self):
        super().__init__()
        self.hr = hm.HitmanReferee()
        self.status = self.hr.start_phase1()
        self.knowledge_hear = {}
        self.map_info = {}
        self.listening_dist = 2
        possible_offset = range(-self.listening_dist, self.listening_dist + 1)
        self.offsets = list(product(possible_offset, possible_offset))
        for i in range(self.status['n']):
            for j in range(self.status['m']):
                self.map_info[(i, j)] = -1
                self.knowledge_hear[(i, j)] = -1
        

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
        observed = self.hr.send_content(self.map_info)
        print("Sending content...")
        print("Observed: {}".format(observed))
    def do_s(self, inp):
        self.do_send()
    
    def help_send(self):
        print("Send content to referee")
    # def help_s(self):
    #     print("Send content to referee")


    def analyse_movement(self):
        if self.status['status'] == "OK":
            self.knowledge_hear[self.status['position']] = self.status['hear']
            for (x, y), content in self.status['vision']:
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
                for i, j in self.offsets:
                    position = (pos_x + i, pos_y + j)
                    if position in self.map_info:
                        self.deduce_listening(position)
            self.deduce_listening(self.status['position'])
            self.print_map()
            self.print_status()
        else:
            print(self.status['status'])


    def deduce_listening(self, position: Tuple[int, int]):
        count, zone = self.get_listening(position)
        if count < 5:
            if count == self.knowledge_hear[position]:
                for i, j in zone:
                    if self.map_info[(i, j)] == -1:
                        self.map_info[(i, j)] = 0


    def get_listening(self, position: Tuple[int, int]) -> Tuple[int, list]:
        count = 0
        x, y = position
        zone = []
        for i, j in self.offsets:
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
                    case 0: print(".", end="")
                    case _: print("?", end="")
            print()


    def do_quit(self, inp):
        print("Quitting...")
        return True
    def do_q(self, inp):
        return self.do_quit(inp)

    def help_quit(self):
        print("Quit the game")


if __name__ == "__main__":
    HitmanDemo().cmdloop()
