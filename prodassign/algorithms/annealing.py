
import wandb
import numpy as np
from tqdm import trange
from colorama import Fore

from prodassign.algorithms.random import RandomSolution
from prodassign.problem import Solution


class AnnealingSolution(RandomSolution):

    def search(self, iterations=2, temperature=1, decay=1e-4, verbose=0) -> Solution:
        sol = self.build()
        sol = sol.optimize_capacities()
        e = sol.energy()
        best = sol
        best_e = best.energy()
        if verbose >= 1:
            print(Fore.YELLOW + f"\n\tInitial best: {best}")   

        pbar = trange(iterations)
        pbar.bar_format = "{l_bar}%s{bar}%s{r_bar}" % (Fore.CYAN, Fore.RESET)
        for i in pbar:
            neighbor = sol.neighbor()
            n_e = neighbor.energy()
            prob = 1.0 if n_e < e else np.exp((e - n_e) / best_e / temperature)
            if prob >= np.random.random():
                if verbose >= 2 and n_e < e:
                    print(f"\n\tBetter found {e:.0f} -> {neighbor}")
                sol = neighbor.optimize_capacities()
                e = sol.energy()

                if sol.price < best.price:
                    best = sol
                    best_e = best.energy()
                    if verbose >= 1:
                        print(Fore.YELLOW + f"\n\tNew best: {best}")
                
                wandb.log({'current_energy': e, 'best_energy': best_e,
                    'current_price': sol.price, 'best_price': best.price,
                    'temperature': temperature, 'transition_probability': prob,
                }, step=i)

            temperature = temperature * (1 - decay)
            pbar.desc = f"{Fore.LIGHTRED_EX}E={e:.2f}{Fore.RESET} | " \
                f"BestE={best_e:.2f} | T={temperature:.1E} | P={prob:.1%} |"
        return best

def main(config):
    problem = AnnealingSolution('data', config['data_fraction'])
    solution = problem.search(
        config['max_iterations'], verbose=1,
        temperature=config['temperature_init'],
        decay=config['temperature_decay']
    )
    print(solution, '\n', repr(solution))
    print(solution.contents_weights())

if __name__ == '__main__':
    config = {
        'data_fraction': 1.0,
        'max_iterations': 4000,

        'temperature_init': 0.5,
        'temperature_decay': 1e-3,
    }

    wandb.init(project='supply_optim', config=config)
    main(wandb.config)
