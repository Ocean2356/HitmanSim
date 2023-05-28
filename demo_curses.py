import referee.hitman.hitman as hm
from itertools import product
from typing import Dict, Tuple
import curses


class HitmanDemoCurses:
    def __init__(self):
        self.hr = hm.HitmanReferee()
        self.status = self.hr.start_phase1()
        self.knowledge = []
        self.map_info = {}
        for i in range(self.status['n']):
            for j in range(self.status['m']):
                self.map_info[(i, j)] = -1

        self.scr = curses.initscr()
        curses.start_color()
        self.h1 = 8
        self.win_map = curses.newwin(self.status['n'], self.status['m']+1, self.h1, 0)
        self.win_status = curses.newwin(10, 30, self.status['n'] + self.h1 + 2, 1)
        self.box = curses.newwin(12, 32, self.status['n'] + self.h1 + 1, 0)

    def main(self, window):
        window.addstr(0, 0, "Welcome to the hitman demo.")
        window.addstr(1, 0, "The map is turned 90 degrees clockwise.")
        window.addstr(2, 0, "w: move forward, a: turn left, d: turn right, q: quit")
        window.addstr(4, 0, "Map size: {}*{}".format(self.status['n'], self.status['m']))
        window.addstr(5, 0, "Guards: {}".format(self.status['guard_count']))
        window.addstr(6, 0, "Civilians: {}".format(self.status['civil_count']))
        self.print_movement(window)
        while True:
            window.refresh()
            key = window.getkey()
            match key:
                case "w": self.status = self.hr.move()
                case "a": self.status = self.hr.turn_anti_clockwise()
                case "d": self.status = self.hr.turn_clockwise()
                case "q": break
                case _: self.status['status'] = "Unknown movement"
            self.print_movement(window)

    def print_movement(self, window):
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
            self.print_map(self.win_map)
        self.print_status(self.win_status)

    def print_map(self, window):
        for i, j in product(range(self.status['n']), range(self.status['m'])):
            content = self.map_info[(i, j)]
            match content:
                case hm.HC.EMPTY: window.addch(i, j, " ")
                case hm.HC.WALL: window.addch(i, j, "#")
                case hm.HC.GUARD_N: window.addch(i, j, "N")
                case hm.HC.GUARD_E: window.addch(i, j, "E")
                case hm.HC.GUARD_S: window.addch(i, j, "S")
                case hm.HC.GUARD_W: window.addch(i, j, "W")
                case hm.HC.CIVIL_N: window.addch(i, j, "n")
                case hm.HC.CIVIL_E: window.addch(i, j, "e")
                case hm.HC.CIVIL_S: window.addch(i, j, "s")
                case hm.HC.CIVIL_W: window.addch(i, j, "w")
                case hm.HC.TARGET: window.addch(i, j, "T")
                case hm.HC.SUIT: window.addch(i, j, "!")
                case hm.HC.PIANO_WIRE: window.addch(i, j, "~")
                case 0: window.addch(i, j, ".")
                case -1: window.addch(i, j, "?")
        x, y = self.status['position']
        attr = curses.A_BOLD
        # window.move(x, y)
        self.scr.move(x + self.h1, y)
        match self.status['orientation']:
            case hm.HC.N: window.addch(x, y, ">", attr)
            case hm.HC.E: window.addch(x, y, "v", attr)
            case hm.HC.S: window.addch(x, y, "<", attr)
            case hm.HC.W: window.addch(x, y, "^", attr)

        window.refresh()
        
    def print_status(self, window):
        self.box.box()
        self.box.refresh()
        window.erase()
        window.addstr(1-1, 0, "Status: {}".format(self.status['status']))
        window.addstr(2-1, 0, "Penalties: {}".format(self.status['penalties']))
        window.addstr(3-1, 0, "Is in guard range: {}".format(self.status['is_in_guard_range']))
        window.addstr(4-1, 0, "Position: {}".format(self.status['position']))
        window.addstr(5-1, 0, "Orientation: {}".format(self.status['orientation']))
        window.addstr(6-1, 0, "Hear: {}".format(self.status['hear']))
        window.addstr(7-1, 0, "Vision: {}".format(len(self.status['vision'])))
        for i, (x, y) in enumerate(self.status['vision']):
            window.addstr(8-1+i, 8, "{},{}".format(x, y))

        window.refresh()

    def get_listening(self, dist=2) -> Tuple[int, list]:
        count = 0
        possible_offset = range(-dist, dist + 1)
        offsets = product(possible_offset, repeat=2)
        x, y = self.status['position']
        zone = []
        for i, j in offsets:
            pos_x, pos_y = x + i, y + j
            if (pos_x, pos_y) not in self.map_info:
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
    

if __name__ == "__main__":
    demo = HitmanDemoCurses()
    curses.wrapper(demo.main)