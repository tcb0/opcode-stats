import json
from typing import Dict, Union, Tuple
import logging

logging.basicConfig(level=logging.DEBUG)


def make_stats(trace_logs: Dict[Tuple[int, int], dict]):
    for (start_block, end_block), tx_opcodes in trace_logs.items():
        dir_path = f"./{start_block}_{end_block}"

        make_opcodes_per_block_stats(tx_opcodes, dir_path)
        make_total_amount_opcodes_stats(tx_opcodes, dir_path)
        make_opcode_counts_stats(tx_opcodes, dir_path)

def make_opcodes_per_block_stats(tx_opcodes: dict, dir_path: str = '.'):
    logging.debug("Calculating opcode per block stats...")
    opcodes_per_block = get_num_opcodes_per_block(tx_opcodes)
    with open(f"{dir_path}/opcodes_per_block.json", "w") as f:
        f.write(json.dumps(opcodes_per_block))
    logging.debug(f"Opcode per block stats calculated and saved to file in  {dir_path} .")


def make_total_amount_opcodes_stats(tx_opcodes: dict, dir_path: str = '.'):
    logging.debug("Calculating total amount opcodes stats...")
    total_amount_opcodes = get_total_amount_of_opcodes_per_block(tx_opcodes)
    with open(f"{dir_path}/total_opcodes_per_block.json", "w") as f:
        f.write(json.dumps(total_amount_opcodes))
    logging.debug(f"Total amount opcode stats calculated and saved to file in  {dir_path} .")


def make_opcode_counts_stats(tx_opcodes: dict, dir_path: str = '.'):
    logging.debug("Calculating opcode counts stats...")
    opcode_counts = get_opcode_counts(tx_opcodes)
    with open(f"{dir_path}/opcode_counts.json", "w") as f:
        f.write(json.dumps(opcode_counts))
    logging.debug(f"Opcode counts stats calculated and saved to file in  {dir_path} .")




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
