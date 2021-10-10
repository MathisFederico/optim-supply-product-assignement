import numpy as np
from prodassign.problem import ProductAssignement, Solution


class GreedySolution(ProductAssignement):

    def build(self):
        products_per_capacities = {capa:[] for capa in self.capacities}
        order = np.argsort([-product.weight for product in self.products])
        self.products = np.take(self.products, order)
        for product in self.products:
            products_per_capacities[self.capacities[1]].append(product)
        return Solution(products_per_capacities, problem=self)

if __name__ == '__main__':
    problem = GreedySolution('data')
    random_solution = problem.build()
    print(random_solution)
