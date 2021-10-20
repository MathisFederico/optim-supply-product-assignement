
import numpy as np
from tqdm import tqdm

from prodassign.problem import FilledCapacity, ProductAssignement, Solution


class PlacingSolution(ProductAssignement):

    def build(self):
        products_per_capacities = {capa:[] for capa in self.capacities}
        order = np.argsort([-product.weight for product in self.products])
        self.products = np.take(self.products, order)

        pallet = self.capacities[1]
        filled_pallets = [FilledCapacity(pallet, [])]
        for product in tqdm(self.products, total=len(self.products)):
            filled_can_take = [filled_pallet.can_take(product) for filled_pallet in filled_pallets]
            try:
                choosen_pallet = filled_can_take.index(True)
                filled_pallets[choosen_pallet] += [product]
            except ValueError:
                filled_pallets.append(FilledCapacity(pallet, [product]))

        for filled_pallet in filled_pallets:
            products_per_capacities[pallet] += filled_pallet.content

        return Solution(products_per_capacities, problem=self)

def main():
    problem = PlacingSolution('data', 1.0)
    solution = problem.build()
    solution = solution.optimize_capacities()
    print(solution)

if __name__ == '__main__':
    main()
