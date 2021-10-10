
import numpy as np
from prodassign.problem import ProductAssignement, Solution


class RandomSolution(ProductAssignement):

    def build(self):
        products_per_capacities = {capa:[] for capa in self.capacities}
        np.random.shuffle(self.products)
        pallet = self.capacities[1]
        for product in self.products:
            products_per_capacities[pallet].append(product)
        return Solution(products_per_capacities, problem=self)

if __name__ == '__main__':
    problem = RandomSolution('data')
    solution = problem.build()
    print(solution.optimize_capacities())
