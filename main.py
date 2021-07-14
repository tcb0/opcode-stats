import json
import os.path

import aiohttp
import asyncio
import api.eth_requests as eth_requests
from typing import Dict, Union, Tuple, List


def get_opcode_counts_from_tx_debug_trace(debug_trace: dict):
    """Parses the debug trace obtained from debug_traceTransaction calls and
    returns a dict with the opcodes appearing in the tx and their counts."""

    opcodes: Dict[str, int] = dict()
    for log in debug_trace.get('structLogs'):
        op_code = log.get('op')
        if op_code in opcodes:
            opcodes[op_code] = opcodes[op_code] + 1
        else:
            opcodes[op_code] = 1

    return opcodes


async def get_opcodes_for_txs(start_block: int, end_block: int, session: aiohttp.ClientSession) -> Dict[int, Dict[str, Dict[str, int]]]:
    """Get opcode counts for transactions that appear in the blocks: [start_block, end_block). """

    data: Dict[int, Dict[str, Dict[str, int]]] = dict()

    for block_num in range(start_block, end_block):
        data[block_num] = dict()

        block_data = eth_requests.get_block_by_number(block_num, True)
        filtered_tx_hashes = get_filtered_tx_hashes(block_data.get('transactions'))

        debug_traces = await asyncio.gather(*[eth_requests.debug_tx_async(tx_hash, session) for tx_hash in filtered_tx_hashes])

        for trace, tx_hash in debug_traces:
            if trace:
                data[block_num][tx_hash] = get_opcode_counts_from_tx_debug_trace(trace)

    return data


def get_filtered_tx_hashes(full_txs: List[Dict]) -> List[str]:
    filtered_tx_hashes = []
    for tx in full_txs:
        if int(tx.get('gas'), 16) == 21000:
            continue

        filtered_tx_hashes.append(tx.get('hash'))

    return filtered_tx_hashes



def get_num_opcodes_per_block(tx_opcodes: Dict[int, Dict[str, Dict[str, int]]], start_block: Union[int, None] = None, end_block: Union[int, None] = None) -> Dict[int, int]:
    """Return the number of unique opcodes (opcode count, not the quantities of each opcode) that appeared in a block.
    The counts are obtained for all transactions in the tx_opcodes dict.
    If start_block and end_block are specified,
    then only the transactions in the [start_block, end_block) range are considered.
    """

    num_opcodes_per_block: Dict[int, int] = dict()

    filtered_opcodes = tx_opcodes

    if start_block and end_block:
        filtered_opcodes = filter_tx_opcodes(tx_opcodes, start_block, end_block)

    for block_num, block_data in filtered_opcodes.items():
        opcodes: Dict[str, int] = dict()

        for tx_hash, tx_data in block_data.items():
            for opcode, count in tx_data.items():
                if opcode not in opcodes:
                    if block_num in num_opcodes_per_block:
                        num_opcodes_per_block[block_num] += 1
                    else:
                        num_opcodes_per_block[block_num] = 1
                    opcodes[opcode] = True

    return num_opcodes_per_block


def get_total_amount_of_opcodes_per_block(tx_opcodes: Dict[int, Dict[str, Dict[str, int]]], start_block: Union[int, None] = None, end_block: Union[int, None] = None) -> Dict[int, int]:
    """Return the total number of opcodes that appear in a block (get the number of operations in a block).
    The counts are obtained for all transactions in the tx_opcodes dict.
    If start_block and end_block are specified,
    then only the transactions in the [start_block, end_block) range are considered.
    """

    total_amount_of_opcodes: Dict[int, int] = dict()
    filtered_opcodes = tx_opcodes

    if start_block and end_block:
        filtered_opcodes = filter_tx_opcodes(tx_opcodes, start_block, end_block)

    for block_num, block_data in filtered_opcodes.items():
        total_amount_of_opcodes[block_num] = 0
        for tx_hash, tx_data in block_data.items():
            for opcode, count in tx_data.items():
                total_amount_of_opcodes[block_num] += count

    return total_amount_of_opcodes


def get_opcode_counts(tx_opcodes: Dict[int, Dict[str, Dict[str, int]]], start_block: Union[int, None] = None, end_block: Union[int, None] = None) -> Dict[str, int]:
    """Return how many times each opcode from the tx_opcodes dict is found.
    If start_block and end_block are specified, then only the transactions
     in the range [start_block, end_block) are considered."""

    opcode_counts: Dict[str, int] = dict()

    filtered_opcodes = tx_opcodes

    if start_block and end_block:
        filtered_opcodes = filter_tx_opcodes(tx_opcodes, start_block, end_block)

    for block_num, block_data in filtered_opcodes.items():

        for tx_hash, tx_data in block_data.items():
            for opcode, count in tx_data.items():
                if opcode not in opcode_counts:
                    opcode_counts[opcode] = count
                else:
                    opcode_counts[opcode] += count

    return opcode_counts


def filter_tx_opcodes(tx_opcodes: Dict[int, Dict[str, Dict[str, int]]], start_block: int, end_block: int) -> Dict[int, Dict[str, Dict[str, int]]]:
    filtered_opcodes = tx_opcodes

    for block_num, block_data in tx_opcodes.items():
        block_num_int = int(block_num)
        if block_num_int >= start_block or block_num_int < end_block:
            filtered_opcodes[block_num] = block_data

    return filtered_opcodes


def get_last_x_block_nums(x: int) -> Tuple[int, int]:
    latest_block = eth_requests.make_call('eth_blockNumber')
    latest_block = int(latest_block, 16)
    return latest_block - x, latest_block


def test():

    # start_block, end_block = get_last_x_block_nums(50)
    res = eth_requests.is_syncing()
    print(res)
    # block_data = eth_requests.get_block_by_number(start_block, False)
    # print(block_data)
    # tx_hash0 = block_data.get('transactions')[5]
    tx_hash0 = '0xecf0b95a24be0ed34e3b0344e9d312e270641cc57677a89943a7c2fa5f7edde2'
    print('tx hash 0', tx_hash0)
    debug_trace = eth_requests.debug_tx(tx_hash0)
    print(debug_trace)


async def main():
    async with aiohttp.ClientSession() as session:
        start_block, end_block = get_last_x_block_nums(100)
        tx_opcode_stats_path = './tx_opcode_stats.json'
        opcodes_per_block_path = './opcodes_per_block.json'
        total_opcodes_per_block_path = './total_opcodes_per_block.json'
        opcode_counts_path = './opcode_counts.json'
        cached = True  # cached = read from file instead parsing each time

        if cached and os.path.isfile((tx_opcode_stats_path)):
            with open(tx_opcode_stats_path, "r") as f:
                tx_opcodes = json.loads(f.read())
        else:
            tx_opcodes = await get_opcodes_for_txs(start_block, end_block, session)
            with open(tx_opcode_stats_path, "w") as f:
                f.write(json.dumps(tx_opcodes))

        print('tx_opcodes_obtained', tx_opcodes)

        opcodes_per_block = get_num_opcodes_per_block(tx_opcodes)
        print('opcodes per block obtained', opcodes_per_block)
        opcode_counts = get_opcode_counts(tx_opcodes)
        print('opcode counts obtained', opcode_counts)

        total_amount_opcodes = get_total_amount_of_opcodes_per_block(tx_opcodes)

        with open(opcodes_per_block_path, "w") as f:
            f.write(json.dumps(opcodes_per_block))

        with open(total_opcodes_per_block_path, "w") as f:
            f.write(json.dumps(total_amount_opcodes))

        with open(opcode_counts_path, "w") as f:
            f.write(json.dumps(opcode_counts))

        print('start block: ', start_block)
        print('end block: ', end_block)


if __name__ == '__main__':
    asyncio.run(main())