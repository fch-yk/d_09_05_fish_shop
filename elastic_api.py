from datetime import datetime

import requests


class ElasticConnection():
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = ""
        self.access_token_expiration_timestamp = 0

    def set_access_token(self):
        if self.access_token:
            current_timestamp = datetime.now().timestamp()
            if current_timestamp > self.access_token_expiration_timestamp:
                print('yes')
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials',
        }

        response = requests.get(
            'https://api.moltin.com/oauth/access_token/',
            data=payload,
            timeout=30,
        )
        response.raise_for_status()
        token_card = response.json()

        self.access_token = token_card['access_token']
        self.access_token_expiration_timestamp = token_card['expires']

    def get_products(self):
        self.set_access_token()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }

        response = requests.get(
            'https://api.moltin.com/pcm/products/',
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_product(self, id):
        self.set_access_token()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }

        response = requests.get(
            f'https://api.moltin.com/catalog/products/{id}/',
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_file_link(self, file_id):
        self.set_access_token()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }

        response = requests.get(
            f'https://api.moltin.com/v2/files/{file_id}/',
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()['data']['link']['href']

    def add_product_to_cart(self, cart_id, product_id, quantity):
        self.set_access_token()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
        payload = {
            "data": {
                "id": product_id,
                "type": "cart_item",
                "quantity": quantity,
            }
        }

        response = requests.post(
            f'https://api.moltin.com/v2/carts/{cart_id}/items/',
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_cart(self, cart_id):
        self.set_access_token()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }
        response = requests.get(
            url=f'https://api.moltin.com/v2/carts/{cart_id}/',
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def get_cart_items(self, cart_id):
        self.set_access_token()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }
        response = requests.get(
            url=f'https://api.moltin.com/v2/carts/{cart_id}/items/',
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def remove_cart_item(self, cart_id, item_id):
        self.set_access_token()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }
        response = requests.delete(
            url=(
                f'https://api.moltin.com/v2/carts/{cart_id}/items/'
                f'{item_id}/'
            ),
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def create_customer(self, name, email):
        self.set_access_token()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
        }
        payload = {
            'data': {
                'type': 'customer',
                'name': name,
                'email': email,
            }
        }
        response = requests.post(
            url='https://api.moltin.com/v2/customers/',
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
