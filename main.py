import json
import os.path

import aiohttp
import asyncio
import api.eth_requests as eth_requests
from src import stats, trace_logs, visualisations, tx_processing
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


def write_tx_hashes(start_block: int, end_block: int, tx_hashes: dict):
    with open(f"./{start_block}_{end_block}/tx_hashes.json", "w") as f:
        f.write(json.dumps(tx_hashes))


def write_opcodes(start_block: int, end_block: int, opcodes: dict):
    with open(f"./{start_block}_{end_block}/tx_opcode_stats.json", "w") as f:
        f.write(json.dumps(opcodes))


def read_tx_hashes(start_block: int, end_block: int):
    with open(f"./{start_block}_{end_block}/tx_hashes.json", "r") as f:
        return json.loads(f.read())


def read_opcodes(start_block: int, end_block: int):
    with open(f"./{start_block}_{end_block}/tx_opcode_stats.json", "r") as f:
        return json.loads(f.read())


def read_all_opcodes(blocks: List[Tuple[int, int]]):
    logs = dict()
    for start_block, end_block in blocks:
        logs[(start_block, end_block)] = read_opcodes(start_block, end_block)

    return logs


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


async def fetch_blocks_tx_hashes(session: aiohttp.ClientSession, blocks: List[Tuple[int, int]]):

    for start_block, end_block in blocks:
        tx_hashes = await tx_processing.get_block_txs(session, start_block, end_block)
        write_tx_hashes(start_block, end_block, tx_hashes)


async def fetch_blocks_debug_logs(session: aiohttp.ClientSession, blocks: List[Tuple[int, int]]):

    for start_block, end_block in blocks:
        tx_hashes = read_tx_hashes(start_block, end_block)
        opcodes = await trace_logs.get_opcodes_for_tx_hashes(session, tx_hashes)
        write_opcodes(start_block, end_block, opcodes)



async def main(fetch_block_data=False):

    latest_block = 12_926_310

    blocks = []
    async with aiohttp.ClientSession() as session:
        if fetch_block_data:
            block_interval_size = 100
            block_interval_difference = 3_000_000
            num_iterations = 4
            for i in range(0, num_iterations):
                print(f'iteration: {i}')
                start_block = latest_block - (block_interval_difference * i) - block_interval_size
                blocks.append((start_block, start_block + block_interval_size))
            #
            with open(f'./{latest_block}.json', 'w') as f:
                f.write(json.dumps(blocks))

            init(blocks)
            logging.debug("Block dirs initiated.")
            await fetch_blocks_tx_hashes(session, blocks)
        else:
            with open(f'./{latest_block}.json', 'r') as f:
                blocks = json.loads(f.read())

        await fetch_blocks_debug_logs(session, blocks)
        logs = read_all_opcodes(blocks)
        block_stats = stats.make_stats(logs)
        visualisations.make_visualisations(block_stats)
    #





if __name__ == '__main__':
    asyncio.run(main(False))
    # test()