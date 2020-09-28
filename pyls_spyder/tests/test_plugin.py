# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# ----------------------------------------------------------------------------

"""pyls-spyder plugin tests."""

# Standard library imports
import os

# PyLS imports
from pyls import uris
from pyls.workspace import Document

# pytest imports
import pytest
from mock import MagicMock

# Local imports
from pyls_spyder.plugin import pyls_document_symbols


DOC_URI = uris.from_fs_path(__file__)
DOC = """
# %%
# -- Imports
import os
import sys

# ------
def a():
    # %%% Cell inside a
    for i in range(0, 10):
        # %%%% Cell
        pass

# %%%
def b():
    # ----- Pass inside b
    pass

# %% Empty cell
# --
"""


@pytest.fixture
def workspace():
    return MagicMock()


@pytest.fixture
def config():
    return MagicMock()


def test_cell_block_symbols(config, workspace):
    document = Document(DOC_URI, workspace, DOC)
    symbols = pyls_document_symbols(config, workspace, document)
    expected = [
        ('Unnamed cell 1', 1, 17, 225),
        ('Imports', 2, 2, 224),
        ('Unnamed comment 1', 6, 6, 224),
        ('Cell inside a', 8, 12, 225),
        ('Cell', 10, 12, 225),
        ('Unnamed cell 2', 13, 17, 225),
        ('Pass inside b', 15, 15, 224),
        ('Empty cell', 18, 19, 225),
        ('Unnamed comment 2', 19, 19, 224)
    ]
    test_results = []
    for symbol in symbols:
        name = symbol['name']
        location = symbol['location']
        sym_range = location['range']
        start = sym_range['start']['line']
        end = sym_range['end']['line']
        kind = symbol['kind']
        test_results.append((name, start, end, kind))
    assert expected == test_results
