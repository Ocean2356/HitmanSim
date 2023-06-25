from sat import *
from ia_phase2 import *
from referee.hitman.hitman import *

def main():
    arbitre = HitmanReferee()
    ai1 = SolveurPhase1(arbitre)
    print("Start phase 1...")
    ai1.executer_phase_1()
    print("Fin phase 1")
    print("Penalites: ", ai1.etat_hitman['malus'])
    carte = ai1.get_carte()
    
    ai2 = AI2(arbitre, carte)

    print("Start phase 2...")
    ai1.executer_phase_1()
    print("Fin phase 2")
    print(ai2.resultat_phase2())


if __name__ == "__main__":
    main()
