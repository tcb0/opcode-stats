import matplotlib.pyplot as plt
import numpy as np
import pandas
import json
import seaborn as sns

from json2html import json2html

from typing import Dict, Tuple
from .utils import StatsType


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

    opcodes = list(opcode_counts.keys())
    counts = list(opcode_counts.values())
    mean = np.mean(counts)

    plt.style.use('fivethirtyeight')

    fig, ax = plt.subplots()
    ax.barh(opcodes, counts, label='Opcode counts')
    ax.legend()

    plt.show()

    fig.savefig(f"charts/{chart_name}.png")


def opcode_frequencies_chart_seaborn(chart_name: str, opcode_frequencies: Dict[str, int], start_block: int, end_block: int):
    opcodes = {k:v for k, v in enumerate(list(opcode_frequencies.keys()))}
    frequencies = {k:v for k, v in enumerate(list(opcode_frequencies.values()))}

    opcode_freq_dict = {"opcode": opcodes, "block_frequency": frequencies}
    opcode_freq_df = pandas.DataFrame.from_dict(opcode_freq_dict)
    sns.set_context(font_scale=0.9)
    sns.set_theme()

    g = sns.catplot(x="opcode", y="block_frequency", kind="bar", data=opcode_freq_df,  palette="crest", height=8, aspect=30/8)
    # plt.tight_layout()
    ax = g.facet_axis(0, 0)

    # iterate through the axes containers
    for c in ax.containers:
        labels = [int(v.get_height()) for v in c]
        ax.bar_label(c, labels=labels, label_type='edge')

    plt.xticks(rotation=90)
    plt.subplots_adjust(bottom=0.25, left=0.03)
    plt.legend(title=f"Opcode frequencies, blocks: {start_block} - {end_block}", loc='upper left')

    plt.show()
    g.savefig(f"charts/{chart_name}.png")

def make_visualisations(blocks_stats: Dict[Tuple[int, int], Dict[StatsType, dict]]):

    for (start_block, end_block), data in blocks_stats.items():
        for stats_type, stats in data.items():
            print("stats type", stats_type)
            if stats_type == StatsType.OPCODES_PER_BLOCK:
                name = f"opcodes_per_block_{start_block}_{end_block}"
                frequencies_chart(name, stats, 'Num opcodes', 'Block number',
                                  f"Unique opcodes per block ({start_block}, {end_block}).", 'Num opcodes')


            elif stats_type == StatsType.TOTAL_AMOUNT_OPCODES:
                name = f"total_opcodes_per_block_{start_block}_{end_block}"
                frequencies_chart(name, stats, 'Num opcodes', 'Block number',
                                  f"Total opcodes per block ({start_block}, {end_block}).", 'Total num opcodes')

            elif stats_type == StatsType.OPCODE_COUNTS:
                name = f"opcode_counts_{start_block}_{end_block}"
                opcode_counts = {k: v for k, v in sorted(stats.items(), reverse=True, key=lambda item: item[1])}
                opcode_count_chart(name, opcode_counts)

                create_opcode_counts_md_table(name, opcode_counts)

                sstats(opcode_counts)
            elif stats_type == StatsType.OPCODE_STATS:
                name = f"opcode_stats_{start_block}_{end_block}"
                create_opcode_stats_md_table(name, stats, start_block, end_block)
            elif stats_type == StatsType.OPCODE_BLOCK_FREQUENCY:
                name = f"opcode_frequencies_{start_block}_{end_block}"
                opcode_frequencies_chart_seaborn(name, stats, start_block, end_block)


def sstats(opcode_counts):
    storage_stats = dict()
    storage_stats['SSTORE'] = opcode_counts.get('SSTORE')
    storage_stats['SLOAD'] = opcode_counts.get('SLOAD')
    with open(f"./stats/sstats.json", "w") as f:
        f.write(json.dumps(storage_stats))


def create_html_table(table_name: str, data: dict):
    table = json2html.convert(data)
    with open(f"./tables/{table_name}.html", "w") as f:
        f.write(table)


def create_opcode_counts_md_table(table_name: str, data: dict):

    table_rows = ["| OPCODE      | Count |", "| ----------- | ----------- |"]
    for key, value in data.items():
        table_rows.append(f"| {key} | {value} |")

    table = "\n".join(table_rows)

    with open(f"./tables/{table_name}.md", "w") as f:
        f.write(table)


def create_opcode_stats_md_table(table_name: str, data: dict, start_block: int, end_block: int):

    table_rows = ["| OPCODE      | Frequency | Frequency percent | Count | Average count per block |", "| ----------- | ----------- | ----------- | ----------- | ----------- |"]
    for key, stats in data.items():
        table_rows.append(f"| **{key}** | {stats['frequency']} | {stats['frequency_percent']}% | {stats['count']} | {stats['avg_count_per_block']} |")

    table = "\n".join(table_rows)
    num_blocks = end_block - start_block
    stats_text = f"""

### Opcode stats for blocks: **{start_block}** - **{end_block}** ({num_blocks} blocks)


#### Legend:
* **Frequency** - In how many blocks the OPCODE appeared
* **Frequency percent** - % of the blocks that the OPCODE appeared in
* **Count** - how many times in total the OPCODE appeared
* **Average** count per block - Count/(Num blocks in range)
    
*Note: the table is sorted by the Count field*

{table}    
    """

    with open(f"./tables/{table_name}.md", "w") as f:
        f.write(stats_text)

