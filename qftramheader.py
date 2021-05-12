import golly as g

s1 = g.getstring("Enter stack size:", "233")
s2 = g.getstring("Enter stdin buffer starting address:", "290")
s3 = g.getstring("Enter stdout buffer starting address:", "790")

RAM_NEGATIVE_BUFFER_SIZE = int(s1)
QFTASM_RAMSTDIN_BUF_STARTPOSITION = int(s2) + RAM_NEGATIVE_BUFFER_SIZE
QFTASM_RAMSTDOUT_BUF_STARTPOSITION = int(s3) + RAM_NEGATIVE_BUFFER_SIZE

RAM_SIZE = 1024
QFTASM_REGAREA_MAX_ADDRESS = 10

p_init = (337, 239)

delta_x = 16
delta_y = 16

d_state2bit = {
    6: 0,
    7: 1,
}

d_bit2state = {
    0: 6,
    1: 7,
}

d_state2chr = {6:"_", 7:"*"}


def getcell_by_index(i_x, i_y):
    return g.getcell(p_init[0] + i_x * delta_x, p_init[1] + i_y * delta_y)

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
            g.setcell(p_init[0] + i_bit * delta_x + x_offset, p_init[1] + addr * delta_y, d_bit2state[int(bit)])

with read("qftramheader_common.py", "rt") as f:
    eval(f.read())
