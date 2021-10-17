
import time
import numpy as np
from tqdm import trange
from colorama import Fore

from prodassign.algorithms.random import RandomSolution
from prodassign.problem import Solution


class AnnealingSolution(RandomSolution):

    def search(self, iterations=2, temperature=100, decay=3e-3, verbose=0) -> Solution:
        sol = self.build()
        e = sol.energy()

        opt_sol = sol.optimize_capacities()
        best = opt_sol

        pbar = trange(iterations)
        pbar.bar_format = "{l_bar}%s{bar}%s{r_bar}" % (Fore.CYAN, Fore.RESET)
        for _ in pbar:
            neighbor = sol.neighbor()
            n_e = neighbor.energy()
            prob = 1.0 if n_e > e else np.exp((n_e - e) * temperature)
            if prob >= np.random.random():
                if verbose >= 2 and n_e > e:
                    print(f"\n\tBetter found {e:.0f} -> {neighbor}")
                sol = neighbor
                e = sol.energy()
                opt_sol = sol.optimize_capacities()

            if opt_sol.price < best.price:
                best = opt_sol
                if verbose >= 1:
                    print(Fore.YELLOW + f"\n\tNew best: {best}")   

            temperature = temperature * (1 - decay)
            pbar.desc = f"{Fore.LIGHTRED_EX}E={e:.2f}{Fore.RESET} | " \
                f"BestE={best.energy():.2f} | T={temperature:.1E} | lP={prob:.1E} |"
        return best

if __name__ == '__main__':
    problem = AnnealingSolution('data', .97)
    solution = problem.search(2000, verbose=1)
    print(solution.contents_weights())
    print(solution, '\n', repr(solution))
