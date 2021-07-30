import aiohttp
import asyncio
from api.eth_requests import get_block_async, get_tx_receipt_async
from typing import Dict, Union, Tuple, List


async def get_block_txs(session: aiohttp.ClientSession, start_block: int, end_block: int):

    blocks_data = await asyncio.gather(*[get_block_async(session, block_number, True) for block_number in range(start_block, end_block)])

    filtered_tx_hashes_per_block = dict()

    for block_data in blocks_data:
        if not block_data:
            continue

        filtered_tx_hashes = get_filtered_tx_hashes(block_data.get('transactions'))
        tx_receipts = await asyncio.gather(*[get_tx_receipt_async(session, tx_hash) for tx_hash in filtered_tx_hashes])

        filtered_tx_hashes = filter_tx_receipts(tx_receipts)
        block_number = int(block_data.get('number'), 16)
        filtered_tx_hashes_per_block[block_number] = filtered_tx_hashes

    return filtered_tx_hashes_per_block


def get_filtered_tx_hashes(full_txs: List[Dict]) -> List[str]:
    filtered_tx_hashes = []
    for tx in full_txs:
        if int(tx.get('gas'), 16) == 21000:
            continue

        filtered_tx_hashes.append(tx.get('hash'))

    return filtered_tx_hashes


def filter_tx_receipts(tx_receipts: List[Dict]) -> List[str]:
    filtered_tx_hashes = []
    for tx_receipt in tx_receipts:
        if tx_receipt.get('status') == '0x0':
            continue

        filtered_tx_hashes.append(tx_receipt.get('transactionHash'))

    return filtered_tx_hashes