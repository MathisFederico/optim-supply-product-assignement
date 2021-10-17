
import os
from typing import Dict, List
from copy import deepcopy

import numpy as np
from colorama import Fore, Style

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

    def __init__(self, path:str, fraction:float=1):
        self.products = [
            Product(*product_data)
            for product_data in load_products_from_csv(os.path.join(path, 'products'))
        ]
        self.capacities = [
            Capacity(*capacity_data)
            for capacity_data in load_transport_options(os.path.join(path, 'capacities'))
        ]
        self.products = self.products[:max(1, int(fraction * len(self.products)))]
        print(f"Loaded problem from: {path} ({fraction:.0%} = {len(self.products)} products)")

class Solution:

    def __init__(self, products_per_capacities: Dict[Capacity, List[Product]],
            problem:ProductAssignement):
        self.products_per_capacities = products_per_capacities
        self.capacities_products = self.compute_capacities()
        self.problem = problem
        self._price = None
        self._energy = None

    def neighbor(self) -> 'Solution':
        products = deepcopy(self.products_per_capacities)
        capacities_with_elements = [
            i for i, capa in enumerate(self.problem.capacities)
            if len(products[capa]) > 0
        ]
        action = np.random.choice(capacities_with_elements + [len(self.problem.capacities)])

        if action < len(self.problem.capacities): 
            p = self.problem.capacities[action]
            if len(products[p]) > 1: # Permute elements of a capacity
                rd_elts = np.random.choice(range(len(products[p])), 2, replace=False)
                products[p][rd_elts[0]], products[p][rd_elts[1]] = \
                    products[p][rd_elts[1]], products[p][rd_elts[0]]
            else:
                other_capa_indexes = list(range(len(self.problem.capacities)))
                other_capa_indexes.remove(action)
                i2 = np.random.choice(other_capa_indexes)

                other_p = self.problem.capacities[i2]
                element = products[p].pop(np.random.randint(len(products[p])))
                products[other_p].append(element)

        else: # Switch element to an other capacity
            i1 = np.random.choice(capacities_with_elements)
            
            other_capa_indexes = list(range(len(self.problem.capacities)))
            other_capa_indexes.remove(i1)
            i2 = np.random.choice(other_capa_indexes)

            p1, p2 = self.problem.capacities[i1], self.problem.capacities[i2]
            element = products[p1].pop()
            products[p2].append(element)

        return Solution(products, self.problem)

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

    def energy(self, weight_energy=0.1, volume_energy=10):
        return - self.price \
            - weight_energy * self.weight_left() \
            - volume_energy * self.volume_left()

    @property
    def price(self):
        if self._price is None:
            self._price = 0
            for capacity, filled_capacities in self.capacities_products.items(): 
                self._price += len(filled_capacities) * capacity.price
        return self._price

    def compute_capacities(self) -> Dict[Capacity, List[FilledCapacity]]:
        capacities_products = {}
        for capacity, products in self.products_per_capacities.items():
            capacity_products = self.fill_capacities(capacity, products)
            capacities_products[capacity] = [
                FilledCapacity(capacity, products)
                for products in capacity_products
            ]
        return capacities_products

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

    def contents_weights(self) -> Dict[Capacity, List[float]]:
        return {
            capa: [filled_capa.weight for filled_capa in self.capacities_products[capa]]
            for capa in self.problem.capacities
        }

    def weight_left(self) -> float:
        weight_left = 0
        contents_weights = self.contents_weights()
        for capa, capa_weights in contents_weights.items():
            weight_left += np.sum(capa.weight - np.array(capa_weights))
        return weight_left

    def contents_volumes(self) -> Dict[Capacity, List[float]]:
        return {
            capa: [filled_capa.volume for filled_capa in self.capacities_products[capa]]
            for capa in self.problem.capacities
        }

    def volume_left(self) -> float:
        volume_left = 0
        contents_volumes = self.contents_volumes()
        for capa, capa_volumes in contents_volumes.items():
            volume_left += np.sum(capa.volume - np.array(capa_volumes))
        return volume_left

    def __str__(self) -> str:
        capa_used = [(capa, len(product_lists))
            for capa, product_lists in self.capacities_products.items()]
        color = Fore.GREEN if self.valid else Fore.RED
        return color + f"Solution {self.price:.0f}$ E={self.energy():.0f} | " + \
            f"{capa_used} | FW:{self.weight_left():.0f} FV:{self.volume_left():.0f}" + \
            Style.RESET_ALL

    def __repr__(self) -> str:
        return str(self.products_per_capacities)

if __name__ == '__main__':
    problem = ProductAssignement('data')
