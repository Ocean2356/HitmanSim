from model_phase1 import *
from vue_phase1_cmd import *

class AI1():
    def __init__(self, model, cl = 0.5, cv = 3, cm = 1, cp = 3, dm = 8):
        self.model = model
        self.penalties_max = model.n * model.m * 1
        self.constant_listening = cl
        self.constant_vision = cv
        self.constant_movement = cm
        self.constant_penalties = cp
        self.depth_max = dm

    def heuristic_listening(self, state: State):
        return (state.position in self.model.knowledge_hear) 

    def heuristic_vision(self, state: State):
        nb_vision = 0
        o = hm.HC(state.orientation)
        x, y = self.model.offsets_orientation[o]
        for i in range(self.model.vision_dist):
            pos_x, pos_y = state.position[0] + x * i, state.position[1] + y * i
            if (pos_x, pos_y) not in self.model.map_info:
                break
            if self.model.map_info[(pos_x, pos_y)] in self.model.Unseen:
                nb_vision += 1
        return nb_vision
        
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

    def heuristic_penalties(self, state: State):
        if self.model.penalties[state.position] > 0:
            return -1 - self.model.penalties[state.position]
        return self.model.penalties[state.position]

    def calculate_movement(self, before: State, after: State):
        if self.model.left(before) == after:
            return "a"
        if self.model.right(before) == after:
            return "d"
        if self.model.forward(before) == after:
            return "w"
        raise Exception("Error in calculate_movement")

    def heuristic(self, current_state: State):
        dict_heuristic = {}
        father_state = {}
        queue = [current_state]
        for i in range(self.depth_max):
            if len(queue) == 0:
                break
            # print("queue", queue)
            tmp_state = queue.pop(0)
            for s in self.model.graph[tmp_state]:
                if s not in self.model.frontier:
                    queue.append(s)
                    if s not in father_state:
                        father_state[s] = tmp_state
                    continue
                if s in dict_heuristic:
                    continue
                l = self.heuristic_listening(s) * self.constant_listening
                v = self.heuristic_vision(s) * self.constant_vision
                m = self.heuristic_movement(s) * self.constant_movement
                p = self.heuristic_penalties(s) * self.constant_penalties
                h = l + v + m + p - i
                dict_heuristic[s] = h
                if s not in father_state:
                    father_state[s] = tmp_state
                # print(s, tmp_state)
        if len(dict_heuristic) == 0:
            return []
        best_state = max(dict_heuristic, key=dict_heuristic.get)
        if dict_heuristic[best_state] < 0:
            return []
        tmp_state = best_state
        movement = []
        # print(dict_heuristic)
        # print(father_state)
        while tmp_state != current_state:
            movement.append(self.calculate_movement(father_state[tmp_state], tmp_state))
            tmp_state = father_state[tmp_state]
        movement.reverse()
        return movement


def main():
    hr = hm.HitmanReferee()
    model = Model1(hr)
    vue = Vue(model)
    ai1 = AI1(model)

    vue.print_map()
    while model.gain > -ai1.penalties_max:
        print("Gain:", model.gain)
        movement = ai1.heuristic(model.state)
        print(movement)
        if len(movement) == 0:
            print("No movement")
            break
        for m in movement:
            model.do_movement(m)
        model.update_graph()
        vue.print_map()

    #  = model.do_send()
    all_correct, score, hist, map_content = model.do_send()
    print("Final gain:", model.gain)

    # model = Model2(hr)

if __name__ == "__main__":
    main()