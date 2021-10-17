import numpy as np
from prodassign.problem import ProductAssignement, Solution


class GreedySolution(ProductAssignement):

    def build(self):
        products_per_capacities = {capa:[] for capa in self.capacities}
        order = np.argsort([-product.weight for product in self.products])
        self.products = np.take(self.products, order)
        pallet = self.capacities[1]
        for product in self.products:
            products_per_capacities[pallet].append(product)
        return Solution(products_per_capacities, problem=self)

if __name__ == '__main__':
    problem = GreedySolution('data', .9)
    solution = problem.build()
    solution = solution.optimize_capacities()
    print(solution)
