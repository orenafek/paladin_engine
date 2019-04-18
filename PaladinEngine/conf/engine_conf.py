"""
    :file: engine_conf.py
    :brief: Configuration for the engine.
    :author: Oren Afek
    :date: 18/04/19
"""
import ast

PALADIN_INLINE_DEFINITION_HEADER = '@@@'
PALADIN_INLINE_DEFINITION_FOOTER = PALADIN_INLINE_DEFINITION_HEADER

# Types of loops.
AST_LOOP_TYPES = [
    ast.For,  # for <target> in <iter>:
    ast.While  # While <cond>
]
