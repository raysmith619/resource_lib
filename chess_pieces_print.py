#chess_pieces_print.py
""" Investigate printing chess piece characters
"""
from select_trace import SlTrace

SlTrace.clearFlags()
SlTrace.setFlags("no_ts")

figure_pieces = {
    'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚',
    'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',
    'fullSQ': chr(0x25A0),
    'emptySQ': chr(0x25A1),
    'black_small_sq' :chr(0x25AA),
    }

for pc in figure_pieces:
    pc_char = figure_pieces[pc]
    pc_char_code = ord(pc_char)
    print(  f"\n {pc}: pc_char:{pc_char} 0x{pc_char_code:4X}")
    SlTrace.lg(f"{pc}: pc_char:{pc_char} 0x{pc_char_code:4X}", replace_non_ascii=None)