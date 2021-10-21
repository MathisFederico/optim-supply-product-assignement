import pickle
import matplotlib.pyplot as plt
import numpy as np

from prodassign.problem import ProductAssignement

with open('benchmark_results.pkl', 'rb') as f:
    algorithms_solutions_later = pickle.load(f)

with open('benchmark_results_2.pkl', 'rb') as f:
    algorithms_solutions = pickle.load(f)

for alg_name, results in algorithms_solutions.items():
    if alg_name in algorithms_solutions_later:
        other_results = algorithms_solutions_later[alg_name]
        max_frac = max(results.keys())
        results.update({frac: res for frac, res in other_results.items() if frac > max_frac})

problem = ProductAssignement('data', 1.0)
algorithms_solutions.pop('greedy')

prices = {}
times = {}
products = {}
fracs = {}

for alg_name, results in algorithms_solutions.items():
    for frac, (sol, time_taken, n_products) in results.items():
        if alg_name not in prices:
            prices[alg_name] = []
            times[alg_name] = []
            products[alg_name] = []
        prices[alg_name].append(sol.price)
        times[alg_name].append(time_taken)
        products[alg_name].append(n_products)


plt.subplot(2, 1, 1)
for alg_name in algorithms_solutions.keys():
    ref_prices = np.array(prices['placing'])[:len(prices[alg_name])]
    dif_prices = np.array(prices[alg_name]) - ref_prices

    plt.semilogx(products[alg_name], -100*dif_prices/ref_prices, label=alg_name,
        linestyle='-', marker='.', alpha=0.6)

plt.title('Savings with respect to the number of products')
plt.ylabel('Savings (%$)')
plt.legend()

plt.subplot(2, 1, 2)
for alg_name in algorithms_solutions.keys():
    plt.loglog(products[alg_name], times[alg_name], label=alg_name,
        linestyle='-', marker='.', alpha=0.6)

plt.title('Time taken with respect to the number of products')
plt.xlabel('Number of products')
plt.ylabel('Time (s)')
plt.legend()
plt.show()
