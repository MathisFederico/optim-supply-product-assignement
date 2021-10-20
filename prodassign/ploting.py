import pickle
import matplotlib.pyplot as plt
import numpy as np

with open('benchmark_results.pkl', 'rb') as f:
    algorithms_solutions = pickle.load(f)

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

plt.subplot(1, 1, 1)
plt.title('Savings with respect to the number of products')
plt.xlabel('Number of products')
plt.ylabel('Savings (%$)')
for alg_name in algorithms_solutions.keys():
    ref_price = np.array(prices['greedy'])
    dif_price = np.array(prices[alg_name]) - ref_price
    rel_dif_price = 100 * dif_price / ref_price
    plt.semilogx(products[alg_name], -rel_dif_price, label=alg_name)

plt.legend()
plt.show()
