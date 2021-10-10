""" Module for data loading """

import numpy as np
import pandas as pd

def confirm_csv(path:str) -> str:
    has_extention = '.' in path
    extention = path.split('.')[-1]
    if not has_extention:
        return path + '.csv'
    if extention != '.csv':
        raise ValueError(f'{path} is not a .csv file')
    return path

def load_products_from_csv(path) -> np.ndarray:
    dataframe = pd.read_csv(confirm_csv(path), sep=';')
    return dataframe[['name', 'weight', 'volume']].to_numpy()

def load_transport_options(path) -> np.ndarray:
    dataframe = pd.read_csv(confirm_csv(path), sep=';')
    return dataframe[['name', 'weight', 'volume', 'price']].to_numpy()

if __name__ == '__main__':
    print("Capacities", load_transport_options('data/capacities'))
    print("Products", load_products_from_csv('data/products'))

