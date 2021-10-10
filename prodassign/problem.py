
import os
from typing import Dict, List
import pprint

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
        self.number_of_capacity_needed = {}
        self.problem = problem
        self.energy = self.compute_energy()

    def neighbor(self, solution:'Solution') -> 'Solution':
        return solution

    def compute_energy(self):
        price = 0
        for capacity, products in self.products_per_capacities.items():
            number_of_capacity_needed = self.number_from_ordered_list(capacity, products)
            self.number_of_capacity_needed[capacity] = number_of_capacity_needed
            price += number_of_capacity_needed * capacity.price
        return -price

    @property
    def valid(self):
        return True

    @staticmethod
    def number_from_ordered_list(capacity:Capacity, products:List[Product]):
        if len(products) == 0:
            return 0

        weight = 0
        number_of_capacity_needed = 1
        for product in products:
            if weight + product.weight > capacity.weight:
                number_of_capacity_needed += 1
                weight = 0
            weight += product.weight
        return number_of_capacity_needed

    def __str__(self) -> str:
        capa_used = [(capa, number) for capa, number in self.number_of_capacity_needed.items()]
        return f"{self.energy} {capa_used}"

    def __repr__(self) -> str:
        return str(self.products_per_capacities)

if __name__ == '__main__':
    problem = ProductAssignement('data')
