
import numpy as np
from prodassign.problem import ProductAssignement, Solution


class RandomSolution(ProductAssignement):

    def build(self, default_capa_id=1):
        products_per_capacities = {capa:[] for capa in self.capacities}
        np.random.shuffle(self.products)
        default_capa = self.capacities[default_capa_id]
        products_per_capacities[default_capa] = self.products
        return Solution(products_per_capacities, problem=self)

def main():
    problem = RandomSolution('data', 1.0)
    solution = problem.build()
    print(solution.optimize_capacities())

if __name__ == '__main__':
    main()
