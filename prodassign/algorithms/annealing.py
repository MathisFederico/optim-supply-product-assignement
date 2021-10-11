
import time
import numpy as np
from tqdm import trange
from colorama import Fore

from prodassign.algorithms.random import RandomSolution
from prodassign.problem import Solution


class AnnealingSolution(RandomSolution):

    def search(self, iterations=2, temperature=10000, decay=5e-4, verbose=0) -> Solution:
        sol = self.build()
        e = sol.energy()

        opt_sol = sol.optimize_capacities()
        opt_e = opt_sol.energy()
        best = opt_sol
        best_e = opt_sol.energy()

        t0 = time.time()

        pbar = trange(iterations)
        pbar.bar_format = "{l_bar}%s{bar}%s{r_bar}" % (Fore.CYAN, Fore.RESET)
        for _ in pbar:
            neighbor = sol.neighbor()
            n_e = neighbor.energy()
            prob = np.exp((n_e - (1.01) * e) / temperature) if n_e < e else 1.0
            if prob >= np.random.random():
                if verbose >= 2 and n_e > e:
                    print(f"\n\tBetter found {e:.0f} -> {neighbor}")
                sol = neighbor
                e = sol.energy()
                opt_sol = sol.optimize_capacities()
                opt_e = opt_sol.energy() 

            if opt_e > best_e:
                best = opt_sol
                best_e = opt_sol.energy()
                if verbose >= 1:
                    print(Fore.YELLOW + f"\n\tNew best: {best}")   

            temperature = temperature * (1 - decay)
            pbar.desc = f"{Fore.LIGHTRED_EX}E={e:.0f}{Fore.RESET} | " \
                f"BestE={best_e:.0f} | T={temperature:.1E} | lP={prob:.1E} |"
        return best

if __name__ == '__main__':
    problem = AnnealingSolution('data')
    solution = problem.search(4000, verbose=1)
    print(solution, '\n', repr(solution))
