import requests
from environs import Env
from pprint import pprint


def main():
    env = Env()
    env.read_env()
    with env.prefixed('ELASTIC_PATH_'):
        elastic_path_client_id = env('CLIENT_ID')
        elastic_path_client_secret = env('CLIENT_SECRET')
    payload = {
        'client_id': elastic_path_client_id,
        'client_secret': elastic_path_client_secret,
        'grant_type': 'client_credentials',
    }

    response = requests.get(
        'https://api.moltin.com/oauth/access_token',
        data=payload,
        timeout=30,
    )
    response.raise_for_status()

    elastic_path_access_token = response.json()['access_token']
    headers = {
        'Authorization': f'Bearer {elastic_path_access_token}',
    }

    response = requests.get(
        'https://api.moltin.com/pcm/products',
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    products = response.json()
    pprint(products)


if __name__ == '__main__':
    main()
