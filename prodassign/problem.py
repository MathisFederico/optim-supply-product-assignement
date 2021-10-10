
import os
from typing import Dict, List
from copy import deepcopy

import numpy as np
from colorama import Fore
from colorama import Style

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

class FilledCapacity:

    def __init__(self, capacity:Capacity, products:List[Product]):
        self.capacity_name = capacity.name
        self.max_weight = capacity.weight
        self.max_volume = capacity.volume
        self.price = capacity.price
        self.content = products

    @property
    def weight(self):
        return sum(product.weight for product in self.content)

    @property
    def volume(self):
        return sum(product.volume for product in self.content)

    @property
    def valid(self):
        return self.weight <= self.max_weight and self.volume <= self.max_volume

    def __add__(self, other):
        self.content += other


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
        raise NotImplementedError

    def optimize_capacities(self) -> 'Solution':
        container, pallet = self.problem.capacities
        products_per_capacities = deepcopy(self.products_per_capacities)
        capacities_products = deepcopy(self.capacities_products)

        if len(capacities_products[pallet]) == 0:
            return Solution(products_per_capacities, problem=self.problem)

        last_pallet_can_fit = self.last_pallet_can_fit(capacities_products)
        while len(capacities_products[pallet]) >= 6 or last_pallet_can_fit:
            last_pallet = capacities_products[pallet].pop()
            if not last_pallet_can_fit:
                capacities_products[container].append(
                    FilledCapacity(container, last_pallet.content))
            else:
                last_container = capacities_products[container][-1]
                last_container.content += last_pallet.content
            self.compute_capacities()
            for product in last_pallet.content:
                products_per_capacities[pallet].remove(product)
                products_per_capacities[container].append(product)
            last_pallet_can_fit = self.last_pallet_can_fit(capacities_products)

        return Solution(products_per_capacities, problem=self.problem)

    def last_pallet_can_fit(self, capacities_products):
        container, pallet = self.problem.capacities
        if len(capacities_products[pallet]) == 0:
            return False

        last_pallet = capacities_products[pallet][-1]
        last_pallet_weight = sum(product.weight for product in last_pallet.content)

        if len(capacities_products[container]) > 0:
            last_container = capacities_products[container][-1]
            last_container_weight = sum(product.weight for product in last_container.content)
        else:
            return False

        return last_pallet_weight + last_container_weight <= container.weight

    def compute_energy(self):
        self.compute_capacities()
        price = 0
        for capacity, filled_capacities in self.capacities_products.items(): 
            price += len(filled_capacities) * capacity.price
        return -price

    def compute_capacities(self):
        for capacity, products in self.products_per_capacities.items():
            capacities_products = self.fill_capacities(capacity, products)
            self.capacities_products[capacity] = [
                FilledCapacity(capacity, products)
                for products in capacities_products
            ]

    @staticmethod
    def fill_capacities(capacity:Capacity, products:List[Product]):
        if len(products) == 0:
            return []

        weight = 0
        volume = 0
        capacities_products = [[]]
        for product in products:
            too_much_weight = weight + product.weight > capacity.weight
            too_much_volume = volume + product.volume > capacity.volume

            if too_much_weight or too_much_volume: # New capacity
                capacities_products.append([])
                weight = 0
                volume = 0

            capacities_products[-1].append(product)
            weight += product.weight
        return capacities_products

    @property
    def valid(self):
        capa_valid = []
        for _, filled_capas in self.capacities_products.items():
            capa_valid.append(np.all(filled_capa.valid for filled_capa in filled_capas))
        return np.all(capa_valid)

    def contents_weights(self):
        return {
            capa: [filled_capa.weight for filled_capa in self.capacities_products[capa]]
            for capa in self.problem.capacities
        }

    def contents_volume(self):
        return {
            capa: [filled_capa.volume for filled_capa in self.capacities_products[capa]]
            for capa in self.problem.capacities
        }

    def __str__(self) -> str:
        capa_used = [(capa, len(product_lists))
            for capa, product_lists in self.capacities_products.items()]
        color = Fore.GREEN if self.valid else Fore.RED
        return color + f"Solution E={self.energy} | {capa_used}" + Style.RESET_ALL

    def __repr__(self) -> str:
        return str(self.products_per_capacities)

if __name__ == '__main__':
    problem = ProductAssignement('data')
