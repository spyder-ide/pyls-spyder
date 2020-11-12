# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# ----------------------------------------------------------------------------

"""pyls-spyder misc utillites."""

# Standard library imports
import re
from typing import Tuple, Optional, Dict


class RegexEvaluator:
    def __init__(self, regex_map: Dict):
        self.regexes = regex_map

    def match(self, string: str) -> Tuple[Optional[str], Optional[re.Match]]:
        re_match = None
        re_rule = None
        for regex_name in self.regexes:
            regex = self.regexes[regex_name]
            re_match = regex.match(string)
            if re_match is not None:
                re_rule = regex_name
                break
        return re_rule, re_match
