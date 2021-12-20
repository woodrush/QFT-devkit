from glife import *
import golly as g


s1 = g.getstring("Enter stack size:", "233")
s2 = g.getstring("Enter stdin buffer starting address:", "290")
s3 = g.getstring("Enter stdout buffer starting address:", "790")

# calc.c
RAM_NEGATIVE_BUFFER_SIZE = int(s1)
QFTASM_RAMSTDIN_BUF_STARTPOSITION = int(s2) + RAM_NEGATIVE_BUFFER_SIZE
QFTASM_RAMSTDOUT_BUF_STARTPOSITION = int(s3) + RAM_NEGATIVE_BUFFER_SIZE

# p_init = (337, 239)
# p_init = (-65648469, -16320387)

delta_x = 16*2048
delta_y = 16*2048

write_locations = [
    (0,0), (0,1), (1,0), (1,1),
    (1751, 1751), (1752, 1751), (1751, 1752), (1752, 1752),
]

write_locations_inv = [
                 (399, 1846), (400, 1846),
    (398, 1847),              (400, 1847),
                 (399, 1848),
]


def getcell_by_index(i_x, i_y):
    boat_displacement = (400, 1847)
    return 1 - g.getcell(
        p_init[0] + i_x * delta_x + boat_displacement[0],
        p_init[1] + i_y * delta_y + boat_displacement[1])

def get_rambyte_by_addr_str(addr):
    bytestring = "".join([str(getcell_by_index(i_x, addr)) for i_x in range(16)])
    return bytestring

def get_rambyte_by_addr_int(addr):
    return int(get_rambyte_by_addr_str(addr), 2)

def show_raw_ram_region(i_x0=0, i_y0=0, i_x1=15, i_y1=32, reverse=False):
    def cell2chr(c):
        d = {0:"_", 1:"*"}
        if c in d.keys():
            return d[c]
        else:
            return "?"

    cells = ["".join([cell2chr(getcell_by_index(i_x, i_y)) for i_x in range(i_x0, i_x1+1)]) for i_y in range(i_y0, i_y1+1)]
    cells = "\n".join(reversed(cells) if reverse else cells)
    ret = g.note(cells)

def show_registers():
    regnames = ["pc", "stdin", "stdout", "a", "b", "c", "d", "bp", "sp", "temp", "temp2"]
    string = ""
    for i_addr, k in enumerate(regnames):
        string += "[{}] {}: {}\n".format(i_addr, regnames[i_addr], get_rambyte_by_addr_int(i_addr))
    g.note(string)

def encode_stdin_string(python_stdin):
    ret = []
    python_stdin_int = [ord(c) for c in python_stdin]
    if len(python_stdin_int) % 2 == 1:
        python_stdin_int = python_stdin_int + [0]

    for i_str, i in enumerate(python_stdin_int):
        # ram[QFTASM_RAMSTDIN_BUF_STARTPOSITION - i_str][0] = ord(c)
        # ram[QFTASM_RAMSTDIN_BUF_STARTPOSITION - i_str][1] += 1
        if i_str % 2 == 0:
            stdin_int = i
        else:
            stdin_int += i << 8

        if i_str % 2 == 1 or i_str == len(python_stdin_int) - 1:
            ret.append(stdin_int)
            # ram[QFTASM_RAMSTDIN_BUF_STARTPOSITION + i_str//2][0] = stdin_int
            # ram[QFTASM_RAMSTDIN_BUF_STARTPOSITION + i_str//2][1] += 1
    return ret

def decode_stdin_buffer(stdin_buf):
    ret = []
    for b in stdin_buf:
        n = b & 0b0000000011111111
        if n == 0:
            break
        ret.append(n)

        n = b >> 8
        if n == 0:
            break
        ret.append(n)

    return "".join([chr(i) for i in ret])

d_bit2state = {
    0: 0,
    1: 1,
}

def write_byte_at(addr, write_byte):
    if addr < 11:
        addr = addr
    # elif addr > 32768:
    #     addr = 32768 - addr + 11
    elif addr >= 1024 - RAM_NEGATIVE_BUFFER_SIZE:
        addr = 1024 - addr + 10
    elif addr >= 11:
        addr = addr + RAM_NEGATIVE_BUFFER_SIZE
    b_binary = "{:016b}".format(write_byte)
    for i_bit, bit in enumerate(b_binary):
        for x_offset in range(2):
            x_offset *= 2048
            for x_p, y_p in write_locations:
                write_x = p_init[0] + i_bit * delta_x + x_offset + x_p
                write_y = p_init[1] + addr * delta_y + y_p
                write_value = int(bit)
                g.setcell(write_x, write_y, write_value)
            for x_p, y_p in write_locations_inv:
                write_x = p_init[0] + i_bit * delta_x + x_offset + x_p
                write_y = p_init[1] + addr * delta_y + y_p
                write_value = 1 - int(bit)
                g.setcell(write_x, write_y, write_value)

def write_ram(stdin_string):
    stdin_bytes = encode_stdin_string(stdin_string)
    # g.note("Raw stdin bytes:" + str(stdin_bytes))
    for i_byte, b in enumerate(stdin_bytes):
        write_byte_at(i_byte + QFTASM_RAMSTDIN_BUF_STARTPOSITION - RAM_NEGATIVE_BUFFER_SIZE, b)

def show_stdio():
    d_state2bit = {
        0: 0,
        1: 1,
    }
    stdin_bitstr = []
    for i_y in range(QFTASM_RAMSTDIN_BUF_STARTPOSITION, QFTASM_RAMSTDOUT_BUF_STARTPOSITION):
        stdin_bitstr.append("".join([str(d_state2bit[getcell_by_index(i_x, i_y)]) for i_x in range(16)]))
    stdin_bytes = [int(s,2) for s in stdin_bitstr]
    stdin_str = decode_stdin_buffer(stdin_bytes)

    g.show("stdin_str")
    g.show(str(len(stdin_str)))
    g.show(stdin_str)
    # TODO: stdout
    stdout_bitstr = ["".join([str(d_state2bit[getcell_by_index(i_x, i_y)]) for i_x in range(16)])
        for i_y in range(QFTASM_RAMSTDOUT_BUF_STARTPOSITION, QFTASM_RAMSTDIN_BUF_STARTPOSITION, -1)
    ]
    stdout_bytes = [int(s,2) for s in stdout_bitstr]
    stdout_bytes_2 = []
    for c in stdout_bytes:
        if c == 0:
            break
        stdout_bytes_2.append(chr(c))
    stdout_str = "".join(stdout_bytes_2)

    g.note("Stdin:\n" + stdin_str + "\n\nStdout:\n" + stdout_str)


s4 = g.getstring("""Enter the coordinates of the top pixel of the hive (the following pattern) at the top-left in the most top-left RAM cell:
(Note: These values change when a pattern with a different ROM size (i.e. a pattern with a different height) is metafied)
_*_
*_*
*_*
_*_""", "-65648599,-13895568")

t4 = tuple(map(int, s4.split(",")))
p_init = (t4[0] + 130, t4[1] + 13)


write_bytes_filepath = g.opendialog("Open CSV for the Initial RAM Values", "CSV files (*.csv)|*.csv")

if write_bytes_filepath:
    with open(write_bytes_filepath, "rt") as f:
        write_bytes = [map(int, line.split(",")) for line in f.readlines()]

    g.show("Writing initial RAM bytes...")
    for t in write_bytes:
        write_byte_at(*t)
    g.show("Done.")
    g.note("Wrote {} initial RAM bytes.".format(len(write_bytes)))
else:
    g.note("Skipped writing initial RAM bytes.")

show_raw_ram_region()

show_registers()

stdin_string_filepath = g.opendialog("Open the text file to write to the stdin buffer")

if stdin_string_filepath:
    with open(stdin_string_filepath, "rt") as f:
        stdin_string = f.read()
    write_ram(stdin_string)
    g.note("Wrote the following content from {} into the stdin buffer.\n----\n{}".format(stdin_string_filepath, stdin_string))
else:
    g.note("Skipped writing the stdin buffer.")


show_stdio()


