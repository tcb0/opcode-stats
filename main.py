import json
import os.path

import aiohttp
import asyncio
import api.eth_requests as eth_requests
from src import stats, trace_logs, visualisations
from typing import Tuple, List
import logging

logging.basicConfig(level=logging.INFO)


def get_last_x_block_nums(x: int) -> Tuple[int, int]:
    latest_block = eth_requests.make_call('eth_blockNumber')
    latest_block = int(latest_block, 16)
    return latest_block - x, latest_block


def get_latest_block() -> int:
    latest_block = eth_requests.make_call('eth_blockNumber')
    return int(latest_block, 16)




def init(blocks: List[Tuple[int, int]]):
    for start_block, end_block in blocks:
        dir_path = f"./{start_block}_{end_block}"
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

def test():

    # start_block, end_block = get_last_x_block_nums(50)
    res = eth_requests.is_syncing()
    print(res)
    # block_data = eth_requests.get_block_by_number(start_block, False)
    # print(block_data)
    # tx_hash0 = block_data.get('transactions')[5]
    tx_hash0 = '0x768ad90cf6b64dd16840f00c0d980b61dce9701e7eab2f990138bceee621d179'
    print('tx hash 0', tx_hash0)
    debug_trace = eth_requests.debug_tx(tx_hash0)
    print(debug_trace)


async def main():
    latest_block = get_latest_block()

    # start_block, end_block tuples
    # samples of 1000 blocks at different points in history
    # blocks = [(latest_block - 1000, latest_block), (latest_block - 150_000, latest_block - 149_000), (latest_block - 300_000, latest_block - 299_000)]
    # blocks = [(latest_block - 100, latest_block)]
    #
    # with open(f'./{latest_block}.json', 'w') as f:
    #     f.write(json.dumps(blocks))

    with open(f'./12833389.json', 'r') as f:
        blocks = json.loads(f.read())

    init(blocks)
    logging.debug("Block dirs initiated.")

    async with aiohttp.ClientSession() as session:
        logs = await trace_logs.read_trace_logs(blocks, session)
        block_stats = stats.make_stats(logs)
        visualisations.make_visualisations(block_stats)


if __name__ == '__main__':
    asyncio.run(main())
    # test()