
import numpy as np
from prodassign.problem import ProductAssignement, Solution


class RandomSolution(ProductAssignement):

    def build(self):
        products_per_capacities = {capa:[] for capa in self.capacities}
        np.random.shuffle(self.products)
        default_capa = self.capacities[0]
        for product in self.products:
            products_per_capacities[default_capa].append(product)
        return Solution(products_per_capacities, problem=self)

if __name__ == '__main__':
    problem = RandomSolution('data', .9)
    solution = problem.build()
    print(solution)
    print(solution.optimize_capacities())
