
from time import time
import numpy as np
import pickle

from prodassign.algorithms.annealing import AnnealingSolution
from prodassign.algorithms.greedy import GreedySolution
from prodassign.algorithms.random import RandomSolution
from prodassign.algorithms.placing import PlacingSolution


def benchmark(points:int, problem_path:str):
    algorithms = (RandomSolution, GreedySolution, PlacingSolution, AnnealingSolution)
    algorithms_names = ('random', 'greedy', 'placing', 'annealing')
    algorithms_solutions = {name:{} for name in algorithms_names}

    for frac in np.logspace(-2, 0, points, endpoint=True):
        for alg_cls, name in zip(algorithms, algorithms_names):
            alg = alg_cls(problem_path, frac)
            t0 = time()
            sol = alg.build(verbose=0)
            if hasattr(alg, 'search'):
                sol = alg.search(4000, verbose=0)
            # print(sol, sol.optimize_capacities(), sol)
            sol = sol.optimize_capacities()
            time_taken = time() - t0
            print(f"{len(alg.products)}({frac:.2%})|{name}|{time_taken:.2E}s -> {sol}")
            algorithms_solutions[name][frac] = (sol, time_taken, len(alg.products))
        print('-'*50)

    print("Done ! Saving ...", end=' ')
    with open('benchmark_results.pkl', 'wb') as f:
        pickle.dump(algorithms_solutions, f)
    print("done !")

if __name__ == '__main__':
    benchmark(100, 'data')
