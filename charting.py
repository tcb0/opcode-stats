import matplotlib.pyplot as plt
import numpy as np
import json

opcodes_per_block_path = './opcodes_per_block.json'
total_opcodes_per_block_path = './total_opcodes_per_block.json'
opcode_counts_path = './opcode_counts.json'


def draw_chart(chart_name: str, data: dict, y_label: str, x_label: str, title: str, label: str):
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


if __name__ == '__main__':

    with open(opcodes_per_block_path, 'r') as f:
        opcodes_per_block = json.loads(f.read())
        keys = [int(key) for key in opcodes_per_block.keys()]
        start_block, end_block = min(keys), max(keys)

        draw_chart('opcodes_per_block', opcodes_per_block, 'Num opcodes', 'Block number', f"Unique opcodes per block ({start_block}, {end_block}).", 'Num opcodes')


    with open(total_opcodes_per_block_path, 'r') as f:
        total_opcodes_per_block = json.loads(f.read())
        keys = [int(key) for key in total_opcodes_per_block.keys()]
        start_block, end_block = min(keys), max(keys)

        draw_chart('total_opcodes_per_block', total_opcodes_per_block, 'Num opcodes', 'Block number', f"Total opcodes per block ({start_block}, {end_block}).", 'Total num opcodes')


    with open(opcode_counts_path, 'r') as f:
        total_opcodes_per_block = json.loads(f.read())

        draw_chart('opcode_counts', total_opcodes_per_block, 'Opcode frequencies', 'Opcode', f"Opcode frequencies ", 'Opcode frequencies')
