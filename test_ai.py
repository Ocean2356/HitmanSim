from ai_phase1 import *
from ai_phase2 import *

def main():
    print("test programme")
    hr = hm.HitmanReferee()
    model = Model1(hr)
    vue = Vue(model)
    ai1 = AI1(model, cl = 0.5, cv = 3, cm = 1, cp = 3, dm = 8)

    vue.print_map()
    while model.gain > -ai1.penalties_max:
        movement = ai1.heuristic(model.state)
        print(movement)
        if len(movement) == 0:
            print("No movement")
            break
        for m in movement:
            model.do_movement(m)
        model.update_graph()
        vue.print_map()

    all_correct, score, hist, map_content = model.do_send()
    print("Final gain:", model.gain)

    print("\nStart phase 2...")
    ai2 = AI2(hr, map_content)
    ai2.executer_phase2()
    print(ai2.etat_hitman)
    print(ai2.resultat_phase2())

if __name__ == "__main__":
    main()
