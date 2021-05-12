from glife import *
import golly as g

s1 = g.getstring("Enter stack size:", "233")
s2 = g.getstring("Enter stdin buffer starting address:", "290")
s3 = g.getstring("Enter stdout buffer starting address:", "790")

s4 = g.getstring("Enter the coordinates of p_init:", "-65648469,-16320387")

RAM_NEGATIVE_BUFFER_SIZE = int(s1)
QFTASM_RAMSTDIN_BUF_STARTPOSITION = int(s2) + RAM_NEGATIVE_BUFFER_SIZE
QFTASM_RAMSTDOUT_BUF_STARTPOSITION = int(s3) + RAM_NEGATIVE_BUFFER_SIZE

QFTASM_REGAREA_MAX_ADDRESS = 10

p_init = tuple(map(int, s4.split(",")))

OTCAMP_SIZE = 2048

delta_x = 16*OTCAMP_SIZE
delta_y = 16*OTCAMP_SIZE

d_state2bit = {
    0: 0,
    1: 1,
}

d_bit2state = {
    0: 0,
    1: 1,
}

d_state2chr = {0:"_", 1:"*"}


boat_displacement = (400, 1847)

write_offsets = [
    (0,0), (0,1), (1,0), (1,1),
    (1751, 1751), (1752, 1751), (1751, 1752), (1752, 1752),
]

write_offsets_inv = [
                 (399, 1846), (400, 1846),
    (398, 1847),              (400, 1847),
                 (399, 1848),
]


def getcell_by_index(i_x, i_y):
    return 1 - g.getcell(
        p_init[0] + i_x * delta_x + boat_displacement[0],
        p_init[1] + i_y * delta_y + boat_displacement[1])

def write_byte_at(addr, write_byte):
    if addr <= QFTASM_REGAREA_MAX_ADDRESS:
        addr = addr
    elif addr >= RAM_SIZE - RAM_NEGATIVE_BUFFER_SIZE:
        addr = RAM_SIZE - addr + QFTASM_REGAREA_MAX_ADDRESS
    elif addr > QFTASM_REGAREA_MAX_ADDRESS:
        addr = addr + RAM_NEGATIVE_BUFFER_SIZE
    b_binary = "{:016b}".format(write_byte)
    for i_bit, bit in enumerate(b_binary):
        for x_offset in range(2):
            x_offset *= OTCAMP_SIZE
            for x_p, y_p in write_offsets:
                write_x = p_init[0] + i_bit * delta_x + x_offset + x_p
                write_y = p_init[1] + addr * delta_y + y_p
                write_value = int(bit)
                g.setcell(write_x, write_y, write_value)
            for x_p, y_p in write_offsets_inv:
                write_x = p_init[0] + i_bit * delta_x + x_offset + x_p
                write_y = p_init[1] + addr * delta_y + y_p
                write_value = 1 - int(bit)
                g.setcell(write_x, write_y, write_value)

with read("qftramheader_common.py", "rt") as f:
    eval(f.read())
