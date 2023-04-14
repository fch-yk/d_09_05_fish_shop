import requests
from environs import Env


def get_elastic_path_access_token(
    elastic_path_client_id,
    elastic_path_client_secret
):
    payload = {
        'client_id': elastic_path_client_id,
        'client_secret': elastic_path_client_secret,
        'grant_type': 'client_credentials',
    }

    response = requests.get(
        'https://api.moltin.com/oauth/access_token/',
        data=payload,
        timeout=30,
    )
    response.raise_for_status()

    return response.json()['access_token']


def main():
    env = Env()
    env.read_env()
    with env.prefixed('ELASTIC_PATH_'):
        elastic_path_client_id = env('CLIENT_ID')
        elastic_path_client_secret = env('CLIENT_SECRET')

    elastic_path_access_token = get_elastic_path_access_token(
        elastic_path_client_id,
        elastic_path_client_secret
    )
    print(elastic_path_access_token)

    headers = {
        'Authorization': f'Bearer {elastic_path_access_token}',
    }

    response = requests.get(
        'https://api.moltin.com/pcm/products/',
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    products = response.json()

    product_id = products['data'][0]['id']

    headers = {
        'Authorization': f'Bearer {elastic_path_access_token}',
        'Content-Type': 'application/json',
    }
    payload = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": 1
        }
    }

    response = requests.post(
        'https://api.moltin.com/v2/carts/1/items/',
        headers=headers,
        json=payload,
        timeout=30
    )
    print(response.text)
    response.raise_for_status()


if __name__ == '__main__':
    main()
