
import os
import copy
from typing import Dict, List

import numpy as np
from colorama import Fore, Style

from prodassign.loader import load_products_from_csv, load_transport_options


class Product:

    def __init__(self, item_id:int, name:str, weight:float, volume:float) -> None:
        self.item_id = item_id
        self.name = name
        self.weight = weight
        self.volume = volume

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name

    def __eq__(self, other: 'Product') -> bool:
        return hash(other) == hash(self)

    def __hash__(self) -> int:
        return self.item_id

class Capacity(Product):

    def __init__(self, item_id:int, name:str, weight:float, volume:float, price:float) -> None:
        super().__init__(item_id, name, weight, volume)
        self.price = price

class FilledCapacity:

    def __init__(self, capacity:Capacity, products:List[Product], problem:'ProductAssignement'):
        self.capacity = capacity
        self.capacity_name = capacity.name
        self.max_weight = capacity.weight
        self.max_volume = capacity.volume
        self.price = capacity.price
        self.content = products
        self.problem = problem

    @property
    def weight(self):
        return sum(self.problem.products[product_id].weight for product_id in self.content)

    @property
    def volume(self):
        return sum(self.problem.products[product_id].volume for product_id in self.content)

    def can_take(self, product:Product):
        return self.weight + product.weight <= self.max_weight and \
               self.volume + product.volume <= self.max_volume

    @property
    def valid(self):
        return self.weight <= self.max_weight and self.volume <= self.max_volume

    def __repr__(self) -> str:
        return str(self.content)

    def __add__(self, other):
        return FilledCapacity(self.capacity, self.content + other, self.problem)

class ProductAssignement:

    def __init__(self, path:str, fraction:float=1):
        self.products = [
            Product(i, *product_data)
            for i, product_data in enumerate(load_products_from_csv(os.path.join(path, 'products')))
        ]
        self.capacities = [
            Capacity(i, *capacity_data)
            for i, capacity_data in enumerate(load_transport_options(os.path.join(path, 'capacities')))
        ]
        self.products = self.products[:max(1, int(fraction * len(self.products)))]

class Solution:

    def __init__(self, products_per_capacities: Dict[int, List[int]], problem:ProductAssignement):
        self.products_per_capacities = products_per_capacities
        self.problem = problem
        self._price = None
        self._products_per_capacities = None
        self._capacities_products = None

    def neighbor(self) -> 'Solution':
        products = copy.deepcopy(self.products_per_capacities)
        capacities_with_elements = [
            i for i, capa in enumerate(self.problem.capacities)
            if len(products[capa]) > 0
        ]
        action = np.random.choice(capacities_with_elements)
        switch = bool(np.random.randint(2))

        if switch:
            other_capa_indexes = list(range(len(self.problem.capacities)))
            other_capa_indexes.remove(action)
            i2 = np.random.choice(other_capa_indexes)

            p1, p2 = self.problem.capacities[action], self.problem.capacities[i2]
            element = products[p1].pop()
            products[p2].append(element)
        else:
            p = self.problem.capacities[action]
            if len(products[p]) > 1: # Permute two successing elements of a capacity
                elt_1, elt_2 = np.random.choice(range(len(products[p])), 2, replace=False)
                products[p][elt_1], products[p][elt_2] = products[p][elt_2], products[p][elt_1]
            else:
                other_capa_indexes = list(range(len(self.problem.capacities)))
                other_capa_indexes.remove(action)
                i2 = np.random.choice(other_capa_indexes)

                other_p = self.problem.capacities[i2]
                element = products[p].pop()
                products[other_p].append(element)

        return Solution(products, self.problem)

    def optimize_capacities(self):
        container, pallet = self.problem.capacities
        self._price = None
        capacities_products = self.capacities_products

        if len(capacities_products[pallet]) == 0:
            return self

        last_pallet_can_fit = self.last_pallet_can_fit(self.capacities_products)
        while len(capacities_products[pallet]) >= 6 or last_pallet_can_fit:
            last_pallet = capacities_products[pallet][-1]
            for product_id in last_pallet.content[::-1]:
                self.products_per_capacities[pallet].remove(product_id)
                self.products_per_capacities[container].append(product_id)

            capacities_products = self.capacities_products
            last_pallet_can_fit = self.last_pallet_can_fit(capacities_products)

        return self

    def last_pallet_can_fit(self, capacities_products):
        container, pallet = self.problem.capacities
        if len(capacities_products[pallet]) == 0:
            return False

        last_pallet = capacities_products[pallet][-1]
        last_pallet_weight = sum(
            self.problem.products[product_id].weight for product_id in last_pallet.content)

        if len(capacities_products[container]) > 0:
            last_container = capacities_products[container][-1]
            last_container_weight = sum(
                self.problem.products[product_id].weight for product_id in last_container.content)
        else:
            return False

        return last_pallet_weight + last_container_weight <= container.weight

    @property
    def price(self):
        if self._price is None:
            self._price = 0
            for capacity_id, filled_capacities in self.capacities_products.items():
                capacity = self.problem.capacities[capacity_id]
                self._price += len(filled_capacities) * capacity.price
        return self._price

    @property
    def capacities_products(self) -> Dict[Capacity, List[FilledCapacity]]:
        if self._products_per_capacities == self.products_per_capacities:
            return self._capacities_products

        capacities_products = {}
        for capacity_id, products in self.products_per_capacities.items():
            capacity = self.problem.capacities[capacity_id]
            capacity_products = self.fill_capacities(capacity, products)
            capacities_products[capacity_id] = [
                FilledCapacity(capacity, products, self.problem)
                for products in capacity_products
            ]
        self._products_per_capacities = copy.deepcopy(self.products_per_capacities)
        self._capacities_products = capacities_products
        return self._capacities_products

    def fill_capacities(self, capacity:Capacity, products_ids:List[int]):
        if len(products_ids) == 0:
            return []

        weight = 0
        volume = 0
        capacities_products = [[]]

        for product_id in products_ids:
            product = self.problem.products[product_id]
            too_much_weight = weight + product.weight > capacity.weight
            too_much_volume = volume + product.volume > capacity.volume

            if too_much_weight or too_much_volume: # New capacity
                capacities_products.append([])
                weight = 0
                volume = 0

            capacities_products[-1].append(product_id)
            weight += product.weight
            volume += product.volume

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
        normalization = []
        for capa, capa_weights in contents_weights.items():
            if len(capa_weights) > 0:
                weight_left += np.sum((capa.weight - np.array(capa_weights)[:-2])**2) # Left in all but last
                weight_left += capa_weights[-1] ** 2 # Used in last
            normalization.append(capa.weight)
        return weight_left / min(normalization) ** 2

    def contents_volumes(self) -> Dict[Capacity, List[float]]:
        return {
            capa: [filled_capa.volume for filled_capa in self.capacities_products[capa]]
            for capa in self.problem.capacities
        }

    def volume_left(self) -> float:
        volume_left = 0
        contents_volumes = self.contents_volumes()
        normalization = []
        for capa, capa_volumes in contents_volumes.items():
            if len(capa_volumes) > 0:
                volume_left += np.sum((capa.volume - np.array(capa_volumes)[:-2])**2) # Left in all but last
                volume_left += capa_volumes[-1] ** 2# Used in last
            normalization.append(capa.volume)
        return volume_left / min(normalization) ** 2

    def __str__(self) -> str:
        capa_used = [(self.problem.capacities[capa].name, len(product_lists))
            for capa, product_lists in self.capacities_products.items()]
        color = Fore.GREEN if self.valid else Fore.RED
        return color + f"Solution {self.price:.0f}$ | " + \
            f"{capa_used} | Wleft:{self.weight_left():.1f} Vleft:{self.volume_left():.1f}" + \
            Style.RESET_ALL

    def __repr__(self) -> str:
        return str(self.products_per_capacities)

if __name__ == '__main__':
    problem = ProductAssignement('data')
