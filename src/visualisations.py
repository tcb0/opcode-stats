import matplotlib.pyplot as plt
import numpy as np
import json
from typing import Dict, Tuple
from .utils import StatsType
opcodes_per_block_path = '../opcodes_per_block.json'
total_opcodes_per_block_path = '../total_opcodes_per_block.json'
opcode_counts_path = '../opcode_counts.json'


def frequencies_chart(chart_name: str, data: dict, y_label: str, x_label: str, title: str, label: str):
    keys = list(data.keys())
    values = list(data.values())

    x = np.arange(len(keys))  # the label locations
    width = 0.8

    fig, ax = plt.subplots()
    ax.bar(x, values, width, label=label)

    # Add some text for labels, title and custom x-axis tick labels, etc.

    ax.set_ylabel(y_label)
    ax.set_xlabel(x_label)
    ax.set_title(title)


    ax.set_xticks([])
    ax.set_xticklabels([])
    ax.legend()

    plt.show()

    fig.savefig(f"charts/{chart_name}.png")


def opcode_count_chart(chart_name: str, opcode_counts: Dict[str, int]):

    opcode_counts = {k: v for k, v in sorted(opcode_counts.items(), reverse=True, key=lambda item: item[1])}

    opcodes = list(opcode_counts.keys())
    counts = list(opcode_counts.values())
    mean = np.mean(counts)

    plt.style.use('fivethirtyeight')

    fig, ax = plt.subplots()
    ax.barh(opcodes, counts, label='Opcode counts')
    ax.legend()

    plt.show()

    fig.savefig(f"charts/{chart_name}.png")



def make_charts(blocks_stats: Dict[Tuple[int, int], Dict[StatsType, dict]]):

    for (start_block, end_block), data in blocks_stats.items():
        for stats_type, stats in data.items():
            print("stats type", stats_type)
            if stats_type == StatsType.OPCODES_PER_BLOCK:
                frequencies_chart(f"opcodes_per_block_{start_block}_{end_block}", stats, 'Num opcodes', 'Block number',
                                  f"Unique opcodes per block ({start_block}, {end_block}).", 'Num opcodes')
            elif stats_type == StatsType.TOTAL_AMOUNT_OPCODES:
                frequencies_chart(f"total_opcodes_per_block_{start_block}_{end_block}", stats, 'Num opcodes', 'Block number',
                                  f"Total opcodes per block ({start_block}, {end_block}).", 'Total num opcodes')
            elif stats_type == StatsType.OPCODE_COUNTS:
                opcode_count_chart(f"opcode_counts_{start_block}_{end_block}", stats)


if __name__ == '__main__':

    with open(opcodes_per_block_path, 'r') as f:
        opcodes_per_block = json.loads(f.read())
        keys = [int(key) for key in opcodes_per_block.keys()]
        start_block, end_block = min(keys), max(keys)

        frequencies_chart('opcodes_per_block', opcodes_per_block, 'Num opcodes', 'Block number', f"Unique opcodes per block ({start_block}, {end_block}).", 'Num opcodes')

    with open(total_opcodes_per_block_path, 'r') as f:
        total_opcodes_per_block = json.loads(f.read())
        keys = [int(key) for key in total_opcodes_per_block.keys()]
        start_block, end_block = min(keys), max(keys)

        frequencies_chart('total_opcodes_per_block', total_opcodes_per_block, 'Num opcodes', 'Block number', f"Total opcodes per block ({start_block}, {end_block}).", 'Total num opcodes')

    with open(opcode_counts_path, 'r') as f:
        opcode_counts = json.loads(f.read())
