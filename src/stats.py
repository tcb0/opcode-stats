import json
from typing import Dict, Union, Tuple
import logging
from .utils import StatsType
logging.basicConfig(level=logging.INFO)


def make_stats(trace_logs: Dict[Tuple[int, int], dict]) -> Dict[Tuple[int, int], Dict[StatsType, dict]]:

    stats = dict()

    for (start_block, end_block), tx_opcodes in trace_logs.items():
        dir_path = f"./{start_block}_{end_block}"

        stats[(start_block, end_block)] = dict()

        stats[(start_block, end_block)][StatsType.OPCODES_PER_BLOCK] = make_opcodes_per_block_stats(tx_opcodes, dir_path)
        stats[(start_block, end_block)][StatsType.TOTAL_AMOUNT_OPCODES] = make_total_amount_opcodes_stats(tx_opcodes, dir_path)
        stats[(start_block, end_block)][StatsType.OPCODE_COUNTS] = make_opcode_counts_stats(tx_opcodes, dir_path)
        stats[(start_block, end_block)][StatsType.OPCODE_STATS] = make_opcode_stats(tx_opcodes, dir_path)


    return stats


def make_opcodes_per_block_stats(tx_opcodes: dict, dir_path: str = '.') -> dict:
    logging.debug("Calculating opcode per block stats...")
    opcodes_per_block = get_num_opcodes_per_block(tx_opcodes)
    with open(f"{dir_path}/opcodes_per_block.json", "w") as f:
        f.write(json.dumps(opcodes_per_block))
    logging.debug(f"Opcode per block stats calculated and saved to file in  {dir_path} .")

    return opcodes_per_block


def make_total_amount_opcodes_stats(tx_opcodes: dict, dir_path: str = '.') -> dict:
    logging.debug("Calculating total amount opcodes stats...")
    total_amount_opcodes = get_total_amount_of_opcodes_per_block(tx_opcodes)
    with open(f"{dir_path}/total_opcodes_per_block.json", "w") as f:
        f.write(json.dumps(total_amount_opcodes))
    logging.debug(f"Total amount opcode stats calculated and saved to file in  {dir_path} .")

    return total_amount_opcodes


def make_opcode_counts_stats(tx_opcodes: dict, dir_path: str = '.') -> dict:
    logging.debug("Calculating opcode counts stats...")
    opcode_counts = get_opcode_counts(tx_opcodes)
    with open(f"{dir_path}/opcode_counts.json", "w") as f:
        f.write(json.dumps(opcode_counts))
    logging.debug(f"Opcode counts stats calculated and saved to file in  {dir_path} .")

    return opcode_counts


def make_opcode_stats(tx_opcodes: dict, dir_path: str = '.') -> dict:
    logging.debug("Calculating stats...")
    opcode_stats = get_opcode_stats(tx_opcodes)
    with open(f"{dir_path}/opcode_stats.json", "w") as f:
        f.write(json.dumps(opcode_stats))
    logging.debug(f"Opcode stats calculated and saved to file in  {dir_path} .")

    return opcode_stats


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


def get_opcode_stats(tx_opcodes: Dict[int, Dict[str, Dict[str, int]]], start_block: Union[int, None] = None, end_block: Union[int, None] = None) -> Dict[str, dict]:
    """Returns stats for each opcode. The stats contain the following fields:
        - frequency - in how many blocks the specific opcode appeared
        - frequency percent - (frequency)/(num blocks in the range)
        - count - how many times the opcode appeared in the blocks
        - average count per block - (count)/(num blocks in the range)
    """

    opcode_stats: Dict[str, dict] = dict()
    num_blocks = 0

    filtered_opcodes = tx_opcodes

    if start_block and end_block:
        filtered_opcodes = filter_tx_opcodes(tx_opcodes, start_block, end_block)

    for block_num, block_data in filtered_opcodes.items():

        opcodes_block = dict()

        for tx_hash, tx_data in block_data.items():
            for opcode, count in tx_data.items():
                if opcode not in opcode_stats:
                    opcode_stats[opcode] = {
                        'frequency': 0,
                        'frequency_percent': 0,
                        'count': 0,
                        'avg_count_per_block': 0,
                    }

                if opcode not in opcodes_block:
                    opcodes_block[opcode] = 1
                    opcode_stats[opcode]['frequency'] += 1

                opcode_stats[opcode]['count'] += count

        num_blocks += 1

    for opcode in opcode_stats.keys():
        opcode_stats[opcode]['frequency_percent'] = (opcode_stats[opcode]['frequency'] / num_blocks) * 100
        opcode_stats[opcode]['avg_count_per_block'] = opcode_stats[opcode]['count'] / num_blocks

    # sort by count in ascending order
    opcode_stats = {k: v for k, v in sorted(opcode_stats.items(), reverse=True, key=lambda item: item[1]['count'])}

    return opcode_stats


def filter_tx_opcodes(tx_opcodes: Dict[int, Dict[str, Dict[str, int]]], start_block: int, end_block: int) -> Dict[int, Dict[str, Dict[str, int]]]:
    filtered_opcodes = tx_opcodes

    for block_num, block_data in tx_opcodes.items():
        block_num_int = int(block_num)
        if block_num_int >= start_block or block_num_int < end_block:
            filtered_opcodes[block_num] = block_data

    return filtered_opcodes
