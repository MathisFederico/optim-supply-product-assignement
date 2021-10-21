
from time import time
import numpy as np
import pickle

from prodassign.algorithms.annealing import AnnealingSolution
from prodassign.algorithms.greedy import GreedySolution
from prodassign.algorithms.random import RandomSolution
from prodassign.algorithms.placing import PlacingSolution
from prodassign.algorithms.orsolver import SolverSolution


def benchmark(points:int, problem_path:str):
    algorithms = (RandomSolution, GreedySolution, PlacingSolution, AnnealingSolution, SolverSolution)
    algorithms_names = ('random', 'greedy', 'placing', 'annealing', 'solver-b&b')
    algorithms_solutions = {name:{} for name in algorithms_names}

    for i, frac in enumerate(np.logspace(-2, -1.2, points, endpoint=True)):
        alg = RandomSolution(problem_path, frac)
        print(f"{i}/{points} : {len(alg.products)}({frac:.2%})" + '-'*100)
        for alg_cls, name in zip(algorithms, algorithms_names):
            alg = alg_cls(problem_path, frac)
            t0 = time()
            sol = alg.build(verbose=0, max_time=500)
            if hasattr(alg, 'search'):
                sol = alg.search(4000, verbose=0)
            sol = sol.optimize_capacities()
            time_taken = time() - t0
            print(f"\t{name}    \t| {time_taken:.2E}s -> {sol}")
            algorithms_solutions[name][frac] = (sol, time_taken, len(alg.products))

    print("Done ! Saving ...", end=' ')
    with open('benchmark_results_2.pkl', 'wb') as f:
        pickle.dump(algorithms_solutions, f)
    print("done !")

if __name__ == '__main__':
    benchmark(100, 'data')
