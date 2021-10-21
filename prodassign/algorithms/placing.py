import time
import wandb
import numpy as np
from tqdm import tqdm

from prodassign.problem import FilledCapacity, ProductAssignement, Solution


class PlacingSolution(ProductAssignement):

    def build(self, verbose=1, max_time=10):
        products_per_capacities = {capa.item_id:[] for capa in self.capacities}
        order = np.argsort([-product.weight for product in self.products])
        self.products = np.take(self.products, order)

        pallet = self.capacities[1]
        filled_pallets = [FilledCapacity(pallet, [], self)]
        for product in tqdm(self.products, total=len(self.products), disable=verbose<1):
            filled_can_take = [filled_pallet.can_take(product) for filled_pallet in filled_pallets]
            product_id = product.item_id
            try:
                choosen_pallet = filled_can_take.index(True)
                filled_pallets[choosen_pallet] += [product_id]
            except ValueError:
                filled_pallets.append(FilledCapacity(pallet, [product_id], self))

        for filled_pallet in filled_pallets:
            products_per_capacities[pallet.item_id] += filled_pallet.content

        return Solution(products_per_capacities, problem=self)

def main(config):
    problem = PlacingSolution('data', config['data_fraction'])
    solution = problem.build()
    solution.optimize_capacities()
    return solution

if __name__ == '__main__':
    config = {'algorithm': 'placing', 'data_fraction': 0.8}
    wandb.init(project='supply_optim', config=config)

    t0 = time.time()
    solution = main(wandb.config)
    total_time = time.time() - t0
    wandb.log({'total_time': total_time, 'solution_price': solution.price})
    print(solution, '\n', repr(solution))
    print('Weights: ', solution.contents_weights())
