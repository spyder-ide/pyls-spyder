# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# ----------------------------------------------------------------------------

"""pyls-spyder main plugin."""

# Standard library imports
import re
from typing import List, Dict, Tuple

# PyLS imports
from pyls import hookimpl
from pyls.config.config import Config
from pyls.workspace import Workspace, Document

# Local imports
from pyls_spyder.utils import RegexEvaluator

# Code cell regular expressions
CELL_PERCENTAGE, CELL_PERCENTAGE_REGEX = (
    'CELL_PERCENTAGE', re.compile(r'^[\t ]*# ?(%%+)(.*)?$'))
CELL_CODECELL, CELL_CODECELL_REGEX = (
    'CELL_CODECELL', re.compile(r'^[\t ]*# ?(<codecell>)(.*)?$'))
CELL_IN, CELL_IN_REGEX = (
    'CELL_IN', re.compile(r'^[\t ]*# ?(In\[)([^\]\r\n]*)?\]?$'))

CELL_REGEX = RegexEvaluator({
    CELL_PERCENTAGE: CELL_PERCENTAGE_REGEX,
    CELL_CODECELL: CELL_CODECELL_REGEX,
    CELL_IN: CELL_IN_REGEX
})

# Block comment regular expressions
BLOCK_DASH = (
    'BLOCK_DASH', re.compile(r'^[\t ]*# ?-{4}([^-\n\r]?.*)?$'))
BLOCK_HASH = (
    'BLOCK_HASH', re.compile(r'^[\t ]*# ?#{3}([^\#\n\r]?.*)?$'))

BLOCK_REGEX = RegexEvaluator(dict([BLOCK_DASH, BLOCK_HASH]))


def peek_symbol(list: List) -> Tuple:
    if len(list) > 0:
        return list[0]
    else:
        return None, 0, ''


def create_symbol(name: str, document: Document,
                  start_line: int, end_line: int,
                  cell=True) -> Dict:
    kind = 225 if cell else 224
    return {
            'name': name,
            'containerName': '',
            'location': {
                'uri': document.uri,
                'range': {
                    'start': {
                        'line': start_line,
                        'character': 0
                    },
                    'end': {
                        'line': max(end_line - 1, 0),
                        'character': 0
                    }
                }
            },
            'kind': kind
        }


@hookimpl
def pyls_document_symbols(config: Config,
                          workspace: Workspace,
                          document: Document) -> List[Dict]:
    """Cell and block comment extraction."""

    settings = config.plugin_settings('pyls_spyder')
    group_cells = settings.get('group_cells', True)
    enable_block_comments = settings.get('enable_block_comments', True)
    lines = document.lines
    cells = []
    blocks = []

    cell_stack = []
    unnamed_cell = 1
    unnamed_block = 1

    for line_num, line in enumerate(lines):
        cell_rule, cell_match = CELL_REGEX.match(line)
        block_rule, block_match = BLOCK_REGEX.match(line)

        if cell_match is not None:
            percentages = cell_match.group(1)
            cell_name = cell_match.group(2).strip()

            if cell_name == '':
                cell_name = 'Unnamed cell {0}'.format(unnamed_cell)
                unnamed_cell += 1

            if not group_cells or cell_rule != CELL_PERCENTAGE:
                cells.append(create_symbol(
                    cell_name, document, line_num, line_num + 1))
            else:
                current_line, current_level, current_name = peek_symbol(
                    cell_stack)
                cell_level = len(percentages) - 1
                if cell_level > current_level:
                    cell_stack.insert(0, (line_num, cell_level, cell_name))
                else:
                    while current_level >= cell_level:
                        cell_stack.pop(0)
                        cells.append(create_symbol(
                            current_name, document, current_line, line_num))
                        (current_line, current_level,
                            current_name) = peek_symbol(cell_stack)
                    cell_stack.insert(0, (line_num, cell_level, cell_name))
        elif block_match is not None and enable_block_comments:
            block_name = block_match.group(1).strip()
            if block_name == '':
                block_name = 'Unnamed comment {0}'.format(unnamed_block)
                unnamed_block += 1
            blocks.append(create_symbol(
                block_name, document, line_num, line_num + 1, False))

    for line, _, name in cell_stack:
        cells.append(create_symbol(name, document, line, line_num + 1))

    spyder_symbols = cells + blocks
    spyder_symbols = sorted(
        spyder_symbols, key=lambda x: x['location']['range']['start']['line'])
    return spyder_symbols


@hookimpl
def pyls_folding_range(
        config: Config,
        workspace: Workspace,
        document: Document) -> List[Dict]:
    lines = document.lines
    cell_stack = []
    for line_num, line in enumerate(lines):
        cell_rule, cell_match = CELL_REGEX.match(line)
        if cell_match is not None:
            percentages = cell_match.group(1)
