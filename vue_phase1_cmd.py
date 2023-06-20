from model_phase1 import *

class Vue:
    def __init__(self, model: Model):
        self.model = model
        self.style = {
            hm.HC.EMPTY: " ",
            hm.HC.WALL: "█",
            hm.HC.GUARD_N: "N",
            hm.HC.GUARD_E: "E",
            hm.HC.GUARD_S: "S",
            hm.HC.GUARD_W: "W",
            hm.HC.CIVIL_N: "n",
            hm.HC.CIVIL_E: "e",
            hm.HC.CIVIL_S: "s",
            hm.HC.CIVIL_W: "w",
            hm.HC.TARGET: "T",
            hm.HC.SUIT: "%",
            hm.HC.PIANO_WIRE: "~",
            hm.HC.N: "^",
            hm.HC.E: ">",
            hm.HC.S: "v",
            hm.HC.W: "<",
            HC.UNKNOWN: "?",
            HC.NOT_PERSON: ".",
        }

    def print_map(self):
        for i in range(self.model.m - 1, -1, -1):
            for j in range(self.model.n):
                if (j, i) == self.model.status['position']:
                    content = self.model.status['orientation']
                else:
                    content = self.model.map_info[(j, i)]
                print(self.style[content], end="")
                if j == self.model.n - 1:
                    print()