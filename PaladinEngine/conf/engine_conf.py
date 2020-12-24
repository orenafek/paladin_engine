"""
    :file: engine_conf.py
    :brief: Configuration for the engine.
    :author: Oren Afek
    :date: 18/04/19
"""
import ast

PALADIN_INLINE_DEFINITION_HEADER = '@@@'
PALADIN_INLINE_DEFINITION_FOOTER = PALADIN_INLINE_DEFINITION_HEADER

PALADIN_ERROR_FILE_PATH = r'/Users/orenafek/Projects/Paladin/PaladinEngine/PaladinEngine/tests/error.out'
# Types of loops.
AST_LOOP_TYPES = [
    ast.For,  # for <target> in <iter>:
    ast.While  # While <cond>
]

ARCHIVE_PRETTY_TABLE_MAX_ROW_LENGTH = 100  # Characters
