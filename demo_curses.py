import referee.hitman.hitman as hm
from itertools import product
from typing import Dict, Tuple
import curses


class HitmanDemoCurses:
    def __init__(self):
        self.hr = hm.HitmanReferee()
        self.status = self.hr.start_phase1()
        self.n = self.status['n']
        self.m = self.status['m']
        self.knowledge_hear = {}
        self.map_info = {}
        self.listening_dist = 2
        possible_offset = range(-self.listening_dist, self.listening_dist + 1)
        self.offsets = list(product(possible_offset, possible_offset))
        for i in range(self.n):
            for j in range(self.m):
                self.map_info[(i, j)] = -1
                self.knowledge_hear[(i, j)] = -1

        self.scr = curses.initscr()
        curses.start_color()
        self.max_y, self.max_x = self.scr.getmaxyx()
        self.y = [0, 3, 9, max(self.n, 10)+12+1, self.max_y - 1]
        self.x = [0, 30, self.m+5, self.max_x - 1]
        off_y = (self.max_y - self.y[3]) / 3
        off_x = (self.max_x - self.x[1] - 15) / 2
        self.y = [int(i+off_y) for i in self.y]
        self.x = [int(i+off_x) for i in self.x]
        self.win_meta = curses.newwin(self.y[2]-self.y[1], self.max_x-self.x[1], self.y[1], self.x[1])
        self.win_list = curses.newwin(self.y[2]-self.y[1], self.x[1], self.y[1], self.x[0])
        self.win_map = curses.newwin(self.n, self.m+1, self.y[2], self.x[0])
        self.win_status = curses.newwin(10, 30, self.y[2], self.x[2]+1)
        self.boxS = curses.newwin(12, 32, self.y[2]-1, self.x[2])
        self.win_info = curses.newwin(self.max_y - self.y[3] - 5, self.max_x, self.y[3], self.x[0])
        self.info_count = 0
        
        curses.use_default_colors()
        for i in range(0, curses.COLORS-1):
            curses.init_pair(i + 1, -1, i)
            # self.scr.addstr(str(i), curses.color_pair(i))
        self.text_status = ["OK", "Err: invalid move", "Unknown movement"]
        self.status2color = {
            "OK": curses.color_pair(72),
            "Err: invalid move": curses.color_pair(221),
            "Unknown movement": curses.color_pair(203),
        }

    def main(self, window):
        window.addstr(self.y[0]+0, self.x[0]+0, "Welcome to the hitman demo.")
        window.addstr(self.y[0]+1, self.x[0]+0, "The map is turned 90 degrees clockwise.")
        self.print_list(self.win_list)
        self.print_meta(self.win_meta)

        self.analyse_movement()
        while True:
            window.refresh()
            key = window.getkey()
            match key:
                case "w": self.status = self.hr.move()
                case "a": self.status = self.hr.turn_anti_clockwise()
                case "d": self.status = self.hr.turn_clockwise()
                case "s": self.send_content(self.win_info)
                # case "p": self.pause()
                case "q": break
                case _: self.status['status'] = self.text_status[2]
            self.analyse_movement()

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
            self.print_map(self.win_map)
        self.print_status(self.win_status)

    def deduce_listening(self, position: Tuple[int, int]):
        count, zone = self.get_listening(position)
        if count < 5:
            if count == self.knowledge_hear[position]:
                for i, j in zone:
                    if self.map_info[(i, j)] == -1:
                        self.map_info[(i, j)] = 0
    

    def get_listening(self, position: Tuple[int, int]) -> Tuple[int, list]:
        dist = self.listening_dist
        offsets = self.offsets
        count = 0
        x, y = position
        zone = []
        for i, j in offsets:
            pos_x, pos_y = x + i, y + j
            # self.print_info(self.win_info, "pos: {},{}".format(y, j))
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

    # def pause(self):
    #     self.scr.addstr(str(self.hr))
    #     self.scr.refresh()
    #     self.scr.getkey()
    #     self.main(self.scr)

    def send_content(self, window):
        observed = self.hr.send_content(self.map_info)
        self.print_info(window, "*" * 10)
        self.print_info(window, "Content sent")
        self.print_info(window, "Observed: {}".format(observed))
        self.print_info(window, "*" * 10)

    def print_info(self, window, message):
        window.addstr(self.info_count, 0, message)
        self.info_count += 1
        if self.info_count == window.getmaxyx()[0]:
            self.info_count = 0
        window.addstr(self.info_count, 0, " " * (window.getmaxyx()[1]-1))
        # self.scr.move(self.info_count, 0)
        window.refresh()

    def print_list(self, window):
        window.addstr(0, 0, "w: move forward")
        window.addstr(1, 0, "a: turn left")
        window.addstr(2, 0, "d: turn right")
        window.addstr(3, 0, "s: send content")
        window.addstr(4, 0, "q: quit")
        window.refresh()

    def print_meta(self, window):
        window.addstr(0, 0, "Map size: {}*{}".format(self.n, self.m))
        window.addstr(1, 0, "Guards: {}".format(self.status['guard_count']))
        window.addstr(2, 0, "Civilians: {}".format(self.status['civil_count']))
        window.refresh()

    def print_map(self, window):
        for i, j in product(range(self.n), range(self.m)):
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
        attr = curses.A_STANDOUT
        # self.scr.move(x + self.h1, y+1)

        try:
            match self.status['orientation']:
                case hm.HC.N: window.addch(x, y, ">", attr)
                case hm.HC.E: window.addch(x, y, "v", attr)
                case hm.HC.S: window.addch(x, y, "<", attr)
                case hm.HC.W: window.addch(x, y, "^", attr)
        except:
            # self.print_info(self.win_info, "pos: {},{}".format(x, y))
            pass

        window.refresh()
        
    def print_status(self, window):
        self.boxS.box()
        self.boxS.refresh()
        window.erase()
        # attr = self.status2color[self.status['status']]
        if self.status['status'] == self.text_status[0]:
            attr = curses.A_NORMAL
        else:
            attr = curses.A_REVERSE
        window.addstr(1-1, 0, "Status: {}".format(self.status['status']), attr)
        window.addstr(2-1, 0, "Penalties: {}".format(self.status['penalties']))
        window.addstr(3-1, 0, "Is in guard range: {}".format(self.status['is_in_guard_range']))
        window.addstr(4-1, 0, "Position: {}".format(self.status['position']))
        window.addstr(5-1, 0, "Orientation: {}".format(self.status['orientation']))
        window.addstr(6-1, 0, "Hear: {}".format(self.status['hear']))
        window.addstr(7-1, 0, "Vision: {}".format(len(self.status['vision'])))
        for i, (x, y) in enumerate(self.status['vision']):
            window.addstr(8-1+i, 8, "{},{}".format(x, y))
        window.refresh()

if __name__ == "__main__":
    try:
        demo = HitmanDemoCurses()
        curses.wrapper(demo.main)
    except curses.error:
        curses.endwin()
        print("Curses error.")
        print("This game needs at least 50x24 terminal size.")
