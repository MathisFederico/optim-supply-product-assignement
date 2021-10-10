
import os
from typing import Dict, List
from copy import deepcopy

from prodassign.loader import load_products_from_csv, load_transport_options


class Product:

    def __init__(self, name:str, weight:float, volume:float) -> None:
        self.name = name
        self.weight = weight
        self.volume = volume

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other: 'Product') -> bool:
        return other.name == self.name

    def __hash__(self) -> int:
        return hash(self.name)

class Capacity(Product):

    def __init__(self, name:str, weight:float, volume:float, price:float) -> None:
        super().__init__(name, weight, volume)
        self.price = price


class ProductAssignement:

    def __init__(self, path:str):
        self.products = [
            Product(*product_data)
            for product_data in load_products_from_csv(os.path.join(path, 'products'))
        ]
        self.capacities = [
            Capacity(*capacity_data)
            for capacity_data in load_transport_options(os.path.join(path, 'capacities'))
        ]
        print(f"Loaded problem from: {path}")


class Solution:

    def __init__(self, products_per_capacities: Dict[Capacity, List[Product]],
            problem:ProductAssignement):
        self.products_per_capacities = products_per_capacities
        self.capacities_products = {}
        self.problem = problem
        self.energy = self.compute_energy()

    def neighbor(self) -> 'Solution':
        return self

    def optimize_capacities(self) -> 'Solution':
        container, pallet = self.problem.capacities
        products_per_capacities = deepcopy(self.products_per_capacities)
        capacities_products = deepcopy(self.capacities_products)

        if len(capacities_products[pallet]) == 0:
            return Solution(products_per_capacities, problem=self.problem)

        last_palet = capacities_products[pallet][-1]
        last_palet_weight = sum(product.weight for product in last_palet)

        if len(capacities_products[container]) > 0:
            last_container = capacities_products[container][-1]
            last_container_weight = sum(product.weight for product in last_container)
        else:
            last_container_weight = 0

        weight_left = container.weight - last_container_weight

        while (len(capacities_products[pallet]) >= 6 or weight_left <= last_palet_weight) and \
                len(capacities_products[pallet]) > 0:

            last_palet = capacities_products[pallet].pop()
            last_palet_weight = sum(product.weight for product in last_palet)

            if len(capacities_products[container]) > 0:
                last_container = capacities_products[container][-1]
                last_container_weight = sum(product.weight for product in last_container)
            else:
                last_container_weight = 0
            weight_left = container.weight - last_container_weight

            for product in last_palet:
                products_per_capacities[pallet].remove(product)
                products_per_capacities[container].append(product)

        return Solution(products_per_capacities, problem=self.problem)

    def compute_energy(self):
        price = 0
        for capacity, products in self.products_per_capacities.items():
            capacities_products = self.fill_capacities(capacity, products)
            self.capacities_products[capacity] = capacities_products
            price += len(capacities_products) * capacity.price
        return -price

    @property
    def valid(self):
        return True

    @staticmethod
    def fill_capacities(capacity:Capacity, products:List[Product]):
        if len(products) == 0:
            return []

        weight = 0
        capacities_products = [[]]
        for product in products:
            if weight + product.weight > capacity.weight:
                capacities_products.append([])
                weight = 0
            capacities_products[-1].append(product)
            weight += product.weight
        return capacities_products

    def __str__(self) -> str:
        capa_used = [(capa, len(product_lists)) for capa, product_lists in self.capacities_products.items()]
        return f"{self.energy} {capa_used}"

    def __repr__(self) -> str:
        return str(self.products_per_capacities)

if __name__ == '__main__':
    problem = ProductAssignement('data')
