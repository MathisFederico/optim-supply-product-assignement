
import time
import numpy as np
from tqdm import trange
from colorama import Fore

from prodassign.algorithms.random import RandomSolution
from prodassign.problem import Solution


class AnnealingSolution(RandomSolution):

    def search(self, iterations=2, temperature=100, decay=1e-5) -> Solution:
        sol = self.build()
        e = sol.energy()

        opt_sol = sol.optimize_capacities()
        best = opt_sol
        best_e = opt_sol.energy()

        t0 = time.time()

        pbar = trange(iterations)
        pbar.bar_format = "%s{l_bar}%s{bar}%s{r_bar}%s" % \
            (Fore.BLUE, Fore.CYAN, Fore.BLUE, Fore.RESET)
        for _ in pbar:
            neighbor = sol.neighbor()
            n_e = neighbor.energy()
            prob = np.exp((n_e - (1.01) * e) / temperature) if n_e < e else 1.0
            if prob >= np.random.random():
                if n_e > e:
                    print(f"\n\tBetter found {e:.0f} -> {neighbor}")
                sol = neighbor
                e = sol.energy()
                opt_sol = sol.optimize_capacities()
                opt_e = opt_sol.energy() 

            if opt_e > best_e:
                best = opt_sol
                best_e = opt_sol.energy()
                print(Fore.YELLOW + f"\n\tNew best: {best}")   

            temperature = temperature * (1 - decay)
            pbar.desc = f"T={temperature:.2f}|lP={np.log(prob):.2f}"
        return best

if __name__ == '__main__':
    problem = AnnealingSolution('data')
    other_sol = problem.search(20000)
    print(other_sol.optimize_capacities())
