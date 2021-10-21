from ortools.linear_solver import pywraplp

from prodassign.problem import ProductAssignement, Solution


class SolverSolution(ProductAssignement):

    def create_data_model(self):
        data = {}
        data['weights'] = [product.weight for product in self.products]
        data['volumes'] = [product.volume for product in self.products]
        data['products'] = [product.item_id for product in self.products]
        data['bins'] = data['products']
        data['bin_weight_capacity'] = self.capacities[1].weight
        data['bin_volume_capacity'] = self.capacities[1].volume
        return data

    def build(self, verbose=1, max_time=10):
        data = self.create_data_model()

        # Create the mip solver with the SCIP backend.
        solver = pywraplp.Solver.CreateSolver('SCIP')
        solver.SetTimeLimit(1000*max_time)

        # Variables
        # x[i, j] = 1 if item i is packed in bin j.
        x = {}
        for i in data['products']:
            for j in data['bins']:
                x[(i, j)] = solver.IntVar(0, 1, 'x_%i_%i' % (i, j))

        # y[j] = 1 if bin j is used.
        y = {}
        for j in data['bins']:
            y[j] = solver.IntVar(0, 1, 'y[%i]' % j)

        # Constraints
        # Each item must be in exactly one bin.
        for i in data['products']:
            solver.Add(sum(x[i, j] for j in data['bins']) == 1)

        # The amount packed in each bin cannot exceed its weight capacity.
        for j in data['bins']:
            solver.Add(
                sum(x[(i, j)] * data['weights'][i] for i in data['products']) <= y[j] *
                    data['bin_weight_capacity'])

        # The amount packed in each bin cannot exceed its volume capacity.
        for j in data['bins']:
            solver.Add(
                sum(x[(i, j)] * data['volumes'][i] for i in data['products']) <= y[j] *
                    data['bin_volume_capacity'])

        # Objective: minimize the number of bins used.
        solver.Minimize(solver.Sum([y[j] for j in data['bins']]))
        solver.Solve()

        # Build our solution object
        products_per_capacities = {capa.item_id:[] for capa in self.capacities}
        for j in data['bins']:
            if y[j].solution_value() == 1:
                for i in data['products']:
                    if x[i, j].solution_value() > 0:
                        products_per_capacities[1].append(i)

        return Solution(products_per_capacities, self)


if __name__ == '__main__':
    alg = SolverSolution('data', 0.04)
    solution = alg.build()
    print(solution.optimize_capacities())
