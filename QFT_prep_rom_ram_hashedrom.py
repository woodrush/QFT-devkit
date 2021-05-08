from glife import *
import golly as g

from pyparsing import *
import sys

d_patterns_rom_body = {
    "init": (-289+8-8*4, 40),
    "init2": (-289+8-8*4 + 63*8, 40),
    "delta": (8, -8),
    0: pattern("4b2B$4b2D$4bD$B3bF2bD$3BD2F2D$4bD$4bB$4bB!"),
    1: pattern("4b2B$4b2D$2bBbD$BbBbBb2D$BDBD2BbD$4bDB$3bB$4bB!")
}


def int2binstr(n, length):
    return ("{:0" + str(length) + "b}").format(n)

class Parser(object):
    def __init__(self):
        addressing_mode = Optional(Char("ABC")).setParseAction(
            lambda t: {"A": 1, "B": 2, "C": 3}[t[0]] if len(t) > 0 else 0
        )
        integer = (Optional("-") + Word(nums)).setParseAction(
            lambda t: int("".join(t))
        )
        operand = Group(addressing_mode + integer)
        MNZ = Literal("MNZ").setParseAction(lambda t: int2binstr(0, length=3))
        MLZ = Literal("MLZ").setParseAction(lambda t: int2binstr(1, length=3))
        ADD = Literal("ADD").setParseAction(lambda t: int2binstr(2, length=3))
        SUB = Literal("SUB").setParseAction(lambda t: int2binstr(3, length=3))
        # AND = Literal("AND").setParseAction(lambda t: int2binstr(4, length=3))
        SRU = Literal("SRU").setParseAction(lambda t: int2binstr(4, length=3))
        SRE = Literal("SRE").setParseAction(lambda t: int2binstr(5, length=3))
        XOR = Literal("XOR").setParseAction(lambda t: int2binstr(6, length=3))
        ANT = Literal("ANT").setParseAction(lambda t: int2binstr(7, length=3))
        # SL =   Literal("SL").setParseAction(lambda t: int2binstr(8, length=4))
        # SRA = Literal("SRA").setParseAction(lambda t: int2binstr(9, length=4))
        # SRL = Literal("SRL").setParseAction(lambda t: int2binstr(10, length=4))
        opcode = MNZ | MLZ | ADD | SUB | SRU | SRE | XOR | ANT #| SL | SRL | SRA
        lineno = (integer + Literal(".")).setParseAction(
            lambda t: [int(t[0])]
        )
        comment = (Literal(";") + restOfLine).suppress()
        inst = (lineno + opcode + operand + operand + operand + Optional(comment)).setParseAction(
            lambda t: [t]
        )
        self.program = ZeroOrMore(inst)

    def parse_string(self, string):
        return self.program.parseString(string)


g.show("Loading code from clipboard...")

rawcode = g.getclipstr()

g.show("Parsing clipboard...")

parser = Parser()
parsed = parser.parse_string(rawcode)

l_binstring = []

def rev(s):
    return "".join(reversed(s))

d_inst2lineno = {}
d_lineno2inst = {}

for line in parsed:
    lineno, opcode, (d_1, n_1), (d_2, n_2), (d_3, n_3) = line
    d_1, d_2, d_3 = map(lambda n: int2binstr((n + (1 << 16)) % (1 << 16), length=2),  [d_1, d_2, d_3])
    # n_1, n_2 = map(lambda n: int2binstr((n + (1 << 16)) % (1 << 16), length=16), [n_1, n_2])
    n_1 = int2binstr((n_1 + (1 << 16)) % (1 << 16), length=8)
    n_2 = int2binstr((n_2 + (1 << 16)) % (1 << 16), length=16)
    n_3 = int2binstr((n_3 + (1 << 16)) % (1 << 16), length=8)
    bins = [opcode, n_1, d_1, n_2, d_2, n_3, d_3]
    linestr = "".join([rev(s) for s in bins])
    rom_width = 3+8+2+16+2+8+2
    # rom_width = 3+18+18+8+2

    linestr = ("{:0" + str(rom_width) + "b}").format(int(linestr, 2))

    # linestr = ("{:" + str(rom_width) + "b}").format(int(linestr, 2))
    # if "1" not in linestr:
    #     linestr = " "*rom_width

    if linestr not in d_inst2lineno.keys():
        d_inst2lineno[linestr] = []
    
    d_inst2lineno[linestr].append(lineno)
    d_lineno2inst[lineno] = linestr

inst_sorted = sorted(d_inst2lineno.items(), key=lambda x: len(x[1]), reverse=True)
# inst_sorted = sorted(d_inst2lineno.items(), key=lambda x: x[0], reverse=True)

l_binstring = [(a, b) for a, (b, _) in enumerate(inst_sorted)]
d_inst2insthash = dict([(b, a) for a, (b, _) in enumerate(inst_sorted)])
linenolist = sorted(d_lineno2inst.keys())

l_binstring_pc2hash = [(lineno, "{:010b}".format(d_inst2insthash[d_lineno2inst[lineno]])) for lineno in linenolist]

# def revstr(x):
#     h = d_inst2insthash[d_lineno2inst[x]]
#     h_str = "{:10b}".format(h)
#     h_revstr = "".join(reversed(h_str))
#     ret = "{:10b}".format(int(h_revstr, 2))
#     if "1" not in ret:
#         ret = " "*10
#     return ret

# # l_binstring_pc2hash = [(lineno, "".join(reversed("{:010b}".format(d_inst2insthash[d_lineno2inst[lineno]])))) for lineno in linenolist]
# l_binstring_pc2hash = [(lineno, revstr(lineno)) for lineno in linenolist]
# l_binstring_pc2hash = tuple(sorted(l_binstring_pc2hash, key=lambda x: x[1], reverse=True))


g.setrule("Varlife")

g.show("Tiling ROM hashtable 1...")

p_init = d_patterns_rom_body["init"]
delta_x, delta_y = d_patterns_rom_body["delta"]
for i_addr, (_, binstring) in enumerate(l_binstring):
    for i_bit, bit in enumerate(binstring):
        if bit == " ":
            continue
        d_patterns_rom_body[int(bit)].put(p_init[0] + delta_x*i_bit, p_init[1] + i_addr*delta_y, (1,0,0,1,"copy"))

g.show("Done.")


g.show("Tiling ROM hashtable 2...")

p_init = d_patterns_rom_body["init2"]
delta_x, delta_y = d_patterns_rom_body["delta"]
for i_addr, (_, binstring) in enumerate(l_binstring_pc2hash):
    # for i_bit, bit in enumerate(reversed(binstring)):
    for i_bit, bit in enumerate(binstring):
        if bit == " ":
            continue
        d_patterns_rom_body[int(bit)].put(p_init[0] + delta_x*i_bit, p_init[1] + i_addr*delta_y, (1,0,0,1,"copy"))

g.show("Done.")


N_BITS_ROM = 10
N_BITS_RAM = 10

ram_length_in = g.getstring("""ROM size: {}
Input maximum RAM address (RAM size - 1) (3 <= n <= (1 << {})):""".format(len(parsed), N_BITS_RAM))

ram_negative_in = g.getstring("Input negative RAM buffer size:")

# ROM_LENGTH = len(parsed)
ROM_LENGTH = len(l_binstring)
RAM_NEGATIVE_BUFFER_SIZE = int(ram_negative_in)
RAM_POSITIVE_BUFFER_SIZE = int(ram_length_in) + 1
RAM_LENGTH = RAM_NEGATIVE_BUFFER_SIZE + RAM_POSITIVE_BUFFER_SIZE

d_patterns_rom_params = {
    "init": (183-8*8-16-8*6-8*4, 40)
}

# d_patterns_ram_xoffset = 96+8*2
d_patterns_ram_xoffset = 96+8*2-8*7-8*4+16*3

d_patterns_rom_demultiplexer = {
    # The bit patterns must be reversed (the lsb comes leftmost) for the rom
    "d_pattern_mpx_body": {
        "tiletype": "tile_bitpattern",
        "reverse_bitarray": True,
        "init": d_patterns_rom_params["init"],
        "delta": (8, -8),
        "repeats": (N_BITS_ROM, ROM_LENGTH),
        0: pattern("3.DB$4.B$4.D$3BD2F2D$BD2.F2.D$2.B.D$.DB.2D$2.B.2B!"),
        1: pattern("3.DB$4.B$4.D$B.BD2F2D$BD2.F2.D$2.B.D$.DB.2D$2.B.2B!"),

        # There is a footer that must be placed when tiling the ROM's mpx
        "footer": {
            "tiletype": "tile_pattern",
            "init_init": (0, -1), # The offset of the footer
            "delta": (8, -1),
            "repeats": (N_BITS_ROM, 1),
            "pattern": pattern("4.2B!"),
        },
    },
}

def tile_rom_demultiplexer_body(
    l_binstring,
    d_pattern=d_patterns_rom_demultiplexer["d_pattern_mpx_body"],
    xoffset=0,
    h_repeats=N_BITS_ROM):
    p_init = d_pattern["init"]
    p_init = (p_init[0] + xoffset, p_init[1])
    delta_x, delta_y = d_pattern["delta"]
    # h_repeats, v_repeats = d_pattern["repeats"]
    v_repeats = d_pattern["repeats"][1]
    reverse_bitarray = d_pattern["reverse_bitarray"]
    method = d_pattern["method"] if "method" in d_pattern.keys() else "copy"

    for i_addr, (lineno, _) in enumerate(l_binstring):
        bitarray = ("{:0" + str(h_repeats) + "b}").format(lineno)
        if reverse_bitarray:
            bitarray = list(reversed(bitarray))
        
        for i_bit, bit in enumerate(bitarray):
            if bit == " ":
                continue
            d_pattern[int(bit)].put(p_init[0] + delta_x*i_bit, p_init[1] + i_addr*delta_y, A=(1,0,0,1,method))

    if "footer" in d_pattern.keys():
        d_footer = d_pattern["footer"]
        # Get the offset stored in "init" first, and then overwrite it
        x_offset_footer, y_offset_footer = d_footer["init_init"]        
        d_footer["init"] = (p_init[0] + x_offset_footer, p_init[1] + i_addr*delta_y + y_offset_footer)
        tile_pattern(d_footer, h_repeats=h_repeats)


d_patterns_rom = {
    # Skip address 0 for the right side
    "d_pattern_right": {
        "tiletype": "tile_pattern",
        "init": (d_patterns_rom_params["init"][0] + 8 * N_BITS_ROM, d_patterns_rom_params["init"][1] - 8),
        "delta": (8, -8),
        "repeats": (1, (ROM_LENGTH) - 1),
        "pattern": pattern("4.B$4.D$4.2B$3B.B$B2.DBD$4.B$4.D$4.2B!"),
    },

    "d_pattern_left": {
        "tiletype": "tile_pattern",
        "init": (d_patterns_rom_params["init"][0] - 8, d_patterns_rom_params["init"][1]),
        "delta": (8, -8),
        "repeats": (1, ROM_LENGTH),
        "pattern": pattern("4.2B$4.2D$2.B.D$B.B.B.2D$BDBD2B.D$4.DB$3.B$4.B!"),
    },
}

d_pattern_ram_right_mpx_body = {
    "d_pattern_right_mpx_body": {
        "tiletype": "tile_bitpattern",
        "reverse_bitarray": False,
        "init": (d_patterns_ram_xoffset + (N_BITS_RAM - 7) * 8 + 144, 233),
        "delta": (8, 16),
        "repeats": (N_BITS_RAM, RAM_LENGTH),
        0: pattern("""3.2D$4.D$BD2.F$B2D2FD2B$4.D$4.B$4.BD$3.2B.B$3.2D.BD$4.D.B$BD2.F2.D$B
2D2FD2B$4.D$4.B$4.B$3.2B!"""),
        1: pattern("""3.2D$4.D$BD2.F$B2D2FD2B$4.D$4.B$4.BD$3.2B.B$3.2D.BD$4.D.B$BD2.F2.D$B
2D2FDB$4.D$4.B$4.B$3.2B!"""),
    },
}

d_pattern_ram_left_mpx_body = {
    "d_pattern_left_mpx_body": {
        "tiletype": "tile_bitpattern",
        "reverse_bitarray": False,
        "init": (d_patterns_ram_xoffset + 80, 233),
        "delta": (8, 16),
        "repeats": (N_BITS_RAM, RAM_LENGTH),
        0: pattern("""3.2D.BD$4.D.B$BD2.F2.D$B2D2FD2B$4.D$4.B$4.B$3.2B$3.2D$4.D$4.B$3.2B$4.
D$4.B$4.BD$3.2B.B!"""),
        1: pattern("""3.2D.BD$4.D.B$BD2.F2.D$B2D2FDB$4.D$4.B$4.B$3.2B$3.2D$4.D$4.B$3.2B$4.D
$4.B$4.BD$3.2B.B!"""),
        # There is a footer that must be placed when tiling the RAM's mpx
        "footer": {
            "tiletype": "tile_pattern",
            "init": (3, 15), # The offset of the footer
            "delta": (8, -1),
            "repeats": (N_BITS_RAM, 1),
            "pattern": pattern("2B.o!"),
            "method": "and",
        },
    },
}

def tile_ram_demultiplexer_body(d_pattern):
    p_init = d_pattern["init"]
    delta_x, delta_y = d_pattern["delta"]
    h_repeats, v_repeats = d_pattern["repeats"]
    reverse_bitarray = d_pattern["reverse_bitarray"]
    method = d_pattern["method"] if "method" in d_pattern.keys() else "copy"

    i_addr = 0
    while i_addr < 11:
        lineno = i_addr
        bitarray = ("{:0" + str(h_repeats) + "b}").format(lineno)
        if reverse_bitarray:
            bitarray = list(reversed(bitarray))
        
        for i_bit, bit in enumerate(bitarray):
            d_pattern[int(bit)].put(p_init[0] + delta_x*i_bit, p_init[1] + i_addr*delta_y, A=(1,0,0,1,method))
        i_addr += 1

    while i_addr < 11 + RAM_NEGATIVE_BUFFER_SIZE:
        lineno = ((1 << N_BITS_RAM) - 1) - (i_addr - 11)
        bitarray = ("{:0" + str(h_repeats) + "b}").format(lineno)
        if reverse_bitarray:
            bitarray = list(reversed(bitarray))
        
        for i_bit, bit in enumerate(bitarray):
            d_pattern[int(bit)].put(p_init[0] + delta_x*i_bit, p_init[1] + i_addr*delta_y, A=(1,0,0,1,method))
        i_addr += 1

    while i_addr < RAM_NEGATIVE_BUFFER_SIZE + RAM_POSITIVE_BUFFER_SIZE:
        lineno = i_addr - RAM_NEGATIVE_BUFFER_SIZE
        bitarray = ("{:0" + str(h_repeats) + "b}").format(lineno)
        if reverse_bitarray:
            bitarray = list(reversed(bitarray))
        
        for i_bit, bit in enumerate(bitarray):
            d_pattern[int(bit)].put(p_init[0] + delta_x*i_bit, p_init[1] + i_addr*delta_y, A=(1,0,0,1,method))
        i_addr += 1

    if "footer" in d_pattern.keys():
        d_footer = d_pattern["footer"]
        # Get the offset stored in "init" first, and then overwrite it
        x_offset_footer, y_offset_footer = d_footer["init"]        
        d_footer["init"] = (p_init[0] + x_offset_footer, p_init[1] + i_addr*delta_y + y_offset_footer)
        tile_pattern(d_footer)

d_patterns_ram = {
    "d_pattern_ramcell": {
        "tiletype": "tile_pattern",
        "init": (d_patterns_ram_xoffset + (N_BITS_RAM - 7) * 2 * 8 + 208, 232),
        "delta": (16, 16),
        "repeats": (16, RAM_LENGTH),
        "pattern": pattern("""3.2B7.B$3.D4.3B2.B$3.F2.BD2.BD.D$BD2FD2B2D3.2FDB$B2.D.D3.B3.F$4.B.B2.
2B.D.D$3.B2.B.D2.DB.2B$2.2B.2B2.2F.B.B$2.D2.D3.B2.B.D$2.B2.B.BD2.D2.
2B$2.2B2.2B2.2B2.B$B2.D6.B2.D$BD.F3.B4D2FDB$2.2FD3B2D3.F$3.D8.D$3.B7.
2B!"""),
    },

    "d_pattern_ramcell_leftborder": {
        "tiletype": "tile_pattern",
        "init": (d_patterns_ram_xoffset + (N_BITS_RAM - 7) * 2 * 8 + 200, 232),
        "delta": (8, 16),
        "repeats": (1, RAM_LENGTH),
        "pattern": pattern("""4.B$4.B$4.D$B2D2FD2B$BD2.F$4.D$3.2D$3.2B$4.B$5.B$3.BD$BD.2BDBD$B2D.B.
B$4.D.B$3.2D$3.2B!"""),
    },

    "d_pattern_left_mpx_rightborder": {
        "tiletype": "tile_pattern",
        "init": (d_patterns_ram_xoffset + (N_BITS_RAM - 7) * 8 + 136, 232),
        "delta": (8, 16),
        "repeats": (1, RAM_LENGTH),
        "pattern": pattern("""3.2B$3.2D$4.D$BD2.F$B2D2FD2B$4.D$4.B$4.B$3.2B$4.D$4.B$3.DBD$4.B.2B$3.
2B$4.D$4.B!""")
    },

    # address 0 is skipped for this part
    "d_pattern_left_mpx_leftborder": {
        "tiletype": "tile_pattern",
        "init": (d_patterns_ram_xoffset + 72, 232+16),
        "delta": (8, 16),
        "repeats": (1, RAM_LENGTH - 1),
        "pattern": pattern("""3.2B$4.D$4.B$3.DBD$4.B.2B$3.2B$4.D$4.B$3.2B$3.2D$4.D$4.B$3.2B$3.2D$4.
D$4.B!"""),
    },
}


def tile_bitpattern(d_pattern):
    p_init = d_pattern["init"]
    delta_x, delta_y = d_pattern["delta"]
    h_repeats, v_repeats = d_pattern["repeats"]
    reverse_bitarray = d_pattern["reverse_bitarray"]
    method = d_pattern["method"] if "method" in d_pattern.keys() else "copy"

    for i_addr in range(v_repeats):
        bitarray = ("{:0" + str(h_repeats) + "b}").format(i_addr)
        if reverse_bitarray:
            bitarray = list(reversed(bitarray))
        
        for i_bit, bit in enumerate(bitarray):
            d_pattern[int(bit)].put(p_init[0] + delta_x*i_bit, p_init[1] + i_addr*delta_y, A=(1,0,0,1,method))
    
    if "footer" in d_pattern.keys():
        d_footer = d_pattern["footer"]
        # Get the offset stored in "init" first, and then overwrite it
        x_offset_footer, y_offset_footer = d_footer["init"]        
        d_footer["init"] = (p_init[0] + x_offset_footer, p_init[1] + i_addr*delta_y + y_offset_footer)
        tile_pattern(d_footer)


def tile_pattern(d_pattern, h_repeats=None, v_repeats=None, p_init=None, xoffset=0):
    if p_init is None:
        p_init = d_pattern["init"]
    p_init = (p_init[0] + xoffset, p_init[1])
    delta_x, delta_y = d_pattern["delta"]
    # h_repeats, v_repeats = d_pattern["repeats"]
    if h_repeats is None:
        h_repeats = d_pattern["repeats"][0]
    if v_repeats is None:
        v_repeats = d_pattern["repeats"][1]
    method = d_pattern["method"] if "method" in d_pattern.keys() else "copy"

    for i_addr in range(v_repeats):
        for i_bit in range(h_repeats):
            d_pattern["pattern"].put(p_init[0] + delta_x*i_bit, p_init[1] + i_addr*delta_y, A=(1,0,0,1,method))

d_tilefunctions = {
    "tile_bitpattern": tile_bitpattern,
    "tile_pattern": tile_pattern,
}


def tile_module(d_module):
    for _, d in d_module.items():
        tilefunc = d_tilefunctions[d["tiletype"]]
        tilefunc(d)

g.setrule("Varlife")


# ROM
g.show("Tiling ROM demultiplexer...")
tile_module(d_patterns_rom)

tile_rom_demultiplexer_body(l_binstring)

tile_rom_demultiplexer_body(l_binstring_pc2hash, xoffset=32*8, h_repeats=12)
tile_pattern(d_patterns_rom["d_pattern_right"], xoffset=32*8+2*8, v_repeats=len(parsed)-1)
tile_pattern(d_patterns_rom["d_pattern_left"],  xoffset=32*8, v_repeats=len(parsed))

# RAM
g.show("Tiling RAM module...")
tile_module(d_patterns_ram)

tile_ram_demultiplexer_body(d_pattern=d_pattern_ram_left_mpx_body["d_pattern_left_mpx_body"])
tile_ram_demultiplexer_body(d_pattern=d_pattern_ram_right_mpx_body["d_pattern_right_mpx_body"])

g.show("Done.")
