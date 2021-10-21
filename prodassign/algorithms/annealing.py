import time
import wandb
import numpy as np
from tqdm import trange
from colorama import Fore

from prodassign.algorithms.random import RandomSolution
from prodassign.problem import Solution


class AnnealingSolution(RandomSolution):

    def energy(self, solution:Solution, weight_energy=0, volume_energy=0):
        price = solution.price
        weight = solution.weight_left() if weight_energy > 0 else 0
        volume = solution.volume_left() if volume_energy > 0 else 0
        normed_price = price / solution.problem.capacities[1].price / len(solution.problem.products)
        return normed_price + weight_energy * weight + volume_energy * volume

    def search(self, iterations=2, max_time=1e6, verbose=0, temperature=1, decay=1e-4,
            weight_energy=0, volume_energy=0, use_wandb=False) -> Solution:
        sol = self.build(verbose=verbose, max_time=max_time)
        sol.optimize_capacities()
        e = self.energy(sol, weight_energy, volume_energy)
        best = sol
        best_e = self.energy(best, weight_energy, volume_energy)
        if verbose >= 1:
            print(Fore.YELLOW + f"\n\tInitial best: {best}")   

        pbar = trange(iterations, disable=verbose<1)
        pbar.bar_format = "{l_bar}%s{bar}%s{r_bar}" % (Fore.CYAN, Fore.RESET)
        t0 = time.time()
        for i in pbar:
            if time.time() - t0 > max_time:
                break
            neighbor = sol.neighbor()
            n_e = self.energy(neighbor, weight_energy, volume_energy)
            prob = 1.0 if n_e < e else np.exp((e - n_e) / best_e / temperature)
            if prob >= np.random.random():
                if n_e < e:
                    if verbose >= 2:
                        print(f"\n\tBetter found {e:.0f} -> {neighbor}")
                else:
                    neighbor.optimize_capacities()

                sol = neighbor
                e = self.energy(sol, weight_energy, volume_energy)

                if sol.price < best.price:
                    best = sol
                    best_e = e
                    if verbose >= 1:
                        print(Fore.YELLOW + f"\n\tNew best: {best}")

                if use_wandb:
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
        max_time=config['max_time'],
        temperature=config['temperature_init'],
        decay=config['temperature_decay'],
        weight_energy=config['weight_energy'],
        volume_energy=config['volume_energy'],
        use_wandb=True,
    )
    return solution

if __name__ == '__main__':
    config = {
        'algorithm': 'annealing',
        'data_fraction': 1.0,
        'max_iterations': 100000,
        'max_time': 10,

        'temperature_init': 1,
        'temperature_decay': 1e-4,

        'weight_energy': 0,
        'volume_energy': 0
    }

    wandb.init(project='supply_optim', config=config)

    t0 = time.time()
    solution = main(wandb.config)
    total_time = time.time() - t0
    wandb.log({'total_time': total_time, 'solution_price': solution.price})
    print(solution, '\n', repr(solution))
    print('Weights: ', solution.contents_weights())
