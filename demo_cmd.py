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
        self.knowledge = []
        self.map_info = {}
        for i in range(self.status['n']):
            for j in range(self.status['m']):
                self.map_info[(i, j)] = -1
        
    def preloop(self) -> None:
        print("Welcome to the hitman demo.")
        print("Type help or ? to list commands.")
        print("Starting game...")
        print("Map size: ", self.status['n'], self.status['m'])
        print("Guards: ", self.status['guard_count'])
        print("Civilians: ", self.status['civil_count'])
        self.print_movement()
        return super().preloop()

    def do_movement(self, movement: str):
        match movement[0]:
            case "w": self.status = self.hr.move()
            case "a": self.status = self.hr.turn_anti_clockwise()
            case "d": self.status = self.hr.turn_clockwise()
            case _: self.status['status'] = "Unknown movement, please enter w, a, or d"
        self.print_movement()

    def print_movement(self):
        
        if self.status['status'] == "OK":
            self.knowledge.append(self.status)
            for (x, y), content in self.status['vision']:
                self.map_info[(x, y)] = content
            count, zone = self.get_listening()
            if count < 5:
                if count == self.status['hear']:
                    for i, j in zone:
                        if self.map_info[(i, j)] == -1:
                            self.map_info[(i, j)] = 0
            self.print_map()
            self.print_status()
        else:
            print(self.status['status'])

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
                    print("X", end="")
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
                    case hm.HC.TARGET: print("T", end="")
                    case hm.HC.SUIT: print("S", end="")
                    case hm.HC.PIANO_WIRE: print("P", end="")
                    case 0: print(".", end="")
                    case _: print("?", end="")
            print()

    def get_listening(self, dist=2):
        count = 0
        possible_offset = range(-dist, dist + 1)
        offsets = product(possible_offset, repeat=2)
        x, y = self.status['position']
        zone = []
        for i, j in offsets:
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

    def do_quit(self, inp):
        print("Quitting...")
        return True

if __name__ == "__main__":
    HitmanDemo().cmdloop()