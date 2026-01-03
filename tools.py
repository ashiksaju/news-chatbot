import requests

FAKE_STORE_API = "https://fakestoreapi.com/products"

def fetch_products(query: str):
    products = requests.get(FAKE_STORE_API).json()
    return products