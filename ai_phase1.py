from model_phase1 import *
from vue_phase1_cmd import *

class AI():
    def __init__(self, model):
        self.model = model

    def heuristic_listening(self, state: State):
        return state.position in self.model.knowledge_hear

    def heuristic_vision(self, state: State):
        nb_vision = 0
        x, y = self.model.offsets_orientation[state.orientation]
        for i in range(self.model.vision_dist):
            pos_x, pos_y = state.position[0] + x * i, state.position[1] + y * i
            if (pos_x, pos_y) not in self.model.map_info:
                break
            if self.model.map_info[(pos_x, pos_y)] in self.model.Unseen:
                nb_vision += 1
        
    def heuristic_movement(self, state: State):
        nb_movement = 0
        lst_state = []
        lst_state.append(self.model.left(state))
        lst_state.append(self.model.right(state))
        tmp_state = self.model.forward(state)
        if tmp_state.position in self.model.map_info:
            lst_state.append(self.model.forward(state))
        for state in lst_state:
            if state not in self.model.graph:
                nb_movement += 1
        return nb_movement

    # def heuristic(self, state: State):



def main():
    model = Model()
    vue = Vue(model)

    # while True:
    if True:

        vue.print_map()

if __name__ == "__main__":
    main()