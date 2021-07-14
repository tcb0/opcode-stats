import os
import json
import requests
import aiohttp
from dotenv import load_dotenv
from typing import Union, Any, List, Tuple
load_dotenv()

GETH_URL = os.environ.get('GETH_URL')




def debug_tx_mock(tx_hash: str) -> dict:
    with open('./mock_trace.json', "r") as f:
        content = json.loads(f.read())
    return content


def get_block_by_number(block_num: Union[int, str], full_txs: bool = False) -> dict:
    try:

        if isinstance(block_num, int):
            block_num = hex(block_num)

        url = f"{GETH_URL}"
        body = {
            "id": 1,
            "method": "eth_getBlockByNumber",
            "params": [block_num, full_txs]
        }
        r = requests.post(url, json=body)
        r.raise_for_status()
        data = r.json()
        return data.get('result')
    except Exception as e:
        raise Exception(e)


def get_tx_by_hash(tx_hash: str):
    try:
        url = f"{GETH_URL}"
        body = {
            "id": 4,
            "method": "eth_getTransactionByHash",
            "params": [tx_hash]
        }
        r = requests.post(url, json=body)
        r.raise_for_status()
        print("response", r.content)
        data = r.json()
        print("data", data)
    except Exception as e:
        raise Exception(e)


def debug_tx(tx_hash: str) -> Union[dict, None]:
    try:
        url = f"{GETH_URL}"
        body = {
            "id": 5,
            "method": "debug_traceTransaction",
            "params": [tx_hash]
        }
        r = requests.post(url, json=body)
        r.raise_for_status()
        data = r.json()
        return data.get('result')
    except Exception as e:
        return None


async def debug_tx_async(tx_hash: str, session: aiohttp.ClientSession) -> Tuple[Union[dict, None], str]:
    try:
        url = f"{GETH_URL}"
        body = {
            "id": 5,
            "method": "debug_traceTransaction",
            "params": [tx_hash, {"disableStack": True, "disableMemory": True, "disableStorage": True}]
        }

        async with session.post(url=url, json=body) as response:
            data = await response.json()
            return data.get('result'), tx_hash
    except Exception as e:
        return None, tx_hash


def is_syncing():
    try:
        url = f"{GETH_URL}"
        body = {
            "id": 1,
            "method": "eth_syncing",
            "params": []
        }
        r = requests.post(url, json=body)
        r.raise_for_status()
        data = r.json()
        return data.get('result')
    except Exception as e:
        raise Exception(e)


def make_call(method_name: str, params: list = None) -> Any:
    try:
        params = params if params else []
        url = f"{GETH_URL}"
        body = {
            "id": 1,
            "method": method_name,
            "params": params
        }
        r = requests.post(url, json=body)
        r.raise_for_status()
        data = r.json()
        return data.get('result')
    except Exception as e:
        raise Exception(e)
