
import numpy as np
from prodassign.problem import ProductAssignement, Solution


class RandomSolution(ProductAssignement):

    def build(self):
        products_per_capacities = {capa:[] for capa in self.capacities}
        np.random.shuffle(self.products)
        for product in self.products:
            random_capacity = self.capacities[1]
            products_per_capacities[random_capacity].append(product)
        return Solution(products_per_capacities, problem=self)

if __name__ == '__main__':
    problem = RandomSolution('data')
    random_solution = problem.build()
    print(random_solution)
