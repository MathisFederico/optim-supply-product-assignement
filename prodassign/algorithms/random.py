import time
import wandb
import numpy as np
from prodassign.problem import ProductAssignement, Solution


class RandomSolution(ProductAssignement):

    def build(self, verbose=1, max_time=10):
        products_per_capacities = {capa.item_id:[] for capa in self.capacities}
        products = self.products.copy()
        np.random.shuffle(products)
        pallet = self.capacities[1]
        products_per_capacities[pallet.item_id] = [p.item_id for p in products]
        return Solution(products_per_capacities, problem=self)

def main(config):
    problem = RandomSolution('data', config['data_fraction'])
    solution = problem.build()
    solution.optimize_capacities()
    return solution

if __name__ == '__main__':
    config = {'algorithm': 'random', 'data_fraction': 1.0}
    wandb.init(project='supply_optim', config=config, reinit=True)

    t0 = time.time()
    solution = main(wandb.config)
    total_time = time.time() - t0
    wandb.log({'total_time': total_time, 'solution_price': solution.price})
    print(solution, '\n', repr(solution))
    print(solution, '\n', repr(solution))
    print('Weights: ', solution.contents_weights())
