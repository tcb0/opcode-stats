import json
import os.path

import aiohttp
import asyncio
import api.eth_requests as eth_requests
from typing import Dict, Union, Tuple, List
import logging

logging.basicConfig(level=logging.INFO)


async def read_trace_logs(blocks: List[Tuple[int, int]], session: aiohttp.ClientSession) -> Dict[Tuple[int, int], dict]:
    trace_logs = dict()

    for start_block, end_block in blocks:
        tx_opcode_stats_path = f"./{start_block}_{end_block}/tx_opcode_stats.json"
        if os.path.isfile((tx_opcode_stats_path)):
            with open(tx_opcode_stats_path, "r") as f:
                tx_opcodes = json.loads(f.read())
        else:
            logging.debug(f"Getting trace logs for blocks: {start_block} - {end_block}.")
            tx_opcodes = await get_block_trace_logs(start_block, end_block, session)
            with open(tx_opcode_stats_path, "w") as f:
                f.write(json.dumps(tx_opcodes))

        trace_logs[(start_block, end_block)] = tx_opcodes

        logging.debug(f"Trace logs for blocks: {start_block} - {end_block} read successfully!.")

    return trace_logs


async def get_block_trace_logs(start_block: int, end_block: int, session: aiohttp.ClientSession) -> dict:
    tx_opcodes = await get_opcodes_for_txs(start_block, end_block, session)
    return tx_opcodes


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


