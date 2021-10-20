import time
import numpy as np
import wandb

from prodassign.problem import ProductAssignement, Solution


class GreedySolution(ProductAssignement):

    def build(self, verbose=1):
        products_per_capacities = {capa.item_id:[] for capa in self.capacities}
        order = np.argsort([product.weight for product in self.products])
        self.products = np.take(self.products, order)
        pallet = self.capacities[1]
        for product in self.products:
            products_per_capacities[pallet.item_id].append(product.item_id)
        return Solution(products_per_capacities, problem=self)

def main(config):
    problem = GreedySolution('data', config['data_fraction'])
    solution = problem.build()
    solution.optimize_capacities()
    return solution

if __name__ == '__main__':
    config = {'algorithm': 'greedy', 'data_fraction': 1.0}
    wandb.init(project='supply_optim', config=config)

    t0 = time.time()
    solution = main(wandb.config)
    total_time = time.time() - t0
    wandb.log({'total_time': total_time, 'solution_price': solution.price})
    print(solution, '\n', repr(solution))
    print('Weights: ', solution.contents_weights())
