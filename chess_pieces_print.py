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
    'b_sm_sq' :chr(0x25AA),
    'vert_line' : chr(0xFF5C),
    'horz_line' : chr(0x23AF),
    'light_sq' : chr(0x23AF),
    'black_cx_hatch' : chr(0x25A9),
    '2_per_em' : chr(0x2002),
    '3_per_em' : chr(0x2004),
    '4_per_em' : chr(0x2005),
    '6_per_em' : chr(0x2006),
    'thin_sp' : chr(0x2009),
    'hair_sp' : chr(0x200A),
    'zero_sp' : chr(0x200B),
    'sq_diag' : chr(0x25A7),
}
ncopy = 40
for pc in figure_pieces:
    pc_char = figure_pieces[pc]
    pc_char_code = ord(pc_char)
    #print(  f"\n {pc}: pc_char:'{pc_char}' 0x{pc_char_code:4X}")
    rep_str = ncopy*pc_char
    SlTrace.lg(f"{pc}: pc_char:'{pc_char}' 0x{pc_char_code:4X} '{rep_str}'",
               replace_non_ascii=None)
    
#for i in range(0x2500, 0x25FF):
#    print(f"{i:x}", chr(i), end=",  ")
