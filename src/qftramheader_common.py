def get_rambyte_by_addr_str(addr):
    bytestring = "".join([str(d_state2bit[getcell_by_index(i_x, addr)]) for i_x in range(16)])
    return bytestring

def get_rambyte_by_addr_int(addr):
    return int(get_rambyte_by_addr_str(addr), 2)

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
        if i_str % 2 == 0:
            stdin_int = i
        else:
            stdin_int += i << 8

        if i_str % 2 == 1 or i_str == len(python_stdin_int) - 1:
            ret.append(stdin_int)
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

def write_ram(stdin_string):
    stdin_bytes = encode_stdin_string(stdin_string)
    for i_byte, b in enumerate(stdin_bytes):
        write_byte_at(i_byte + QFTASM_RAMSTDIN_BUF_STARTPOSITION - RAM_NEGATIVE_BUFFER_SIZE, b)

def show_raw_ram_region(i_x0=0, i_y0=0, i_x1=15, i_y1=32, reverse=False):
    def cell2chr(c):
        if c in d_state2chr.keys():
            return d_state2chr[c]
        else:
            return "?"

    cells = ["".join([cell2chr(getcell_by_index(i_x, i_y)) for i_x in range(i_x0, i_x1+1)]) for i_y in range(i_y0, i_y1+1)]
    cells = "\n".join(reversed(cells) if reverse else cells)
    ret = g.note(cells)

def show_stdio():
    stdin_bitstr = []
    for i_y in range(QFTASM_RAMSTDIN_BUF_STARTPOSITION, QFTASM_RAMSTDOUT_BUF_STARTPOSITION):
        stdin_bitstr.append("".join([str(d_state2bit[getcell_by_index(i_x, i_y)]) for i_x in range(16)]))
    stdin_bytes = [int(s,2) for s in stdin_bitstr]
    stdin_str = decode_stdin_buffer(stdin_bytes)

    g.show("stdin_str")
    g.show(str(len(stdin_str)))
    g.show(stdin_str)
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

def write_initial_ram():
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

def write_stdin_buffer():
    stdin_string_filepath = g.opendialog("Open the text file to write to the stdin buffer")

    if stdin_string_filepath:
        with open(stdin_string_filepath, "rt") as f:
            stdin_string = f.read()
        write_ram(stdin_string)
        g.note("Wrote into the stdin buffer.\nFilepath:\n{}\nContent:\n{}".format(stdin_string_filepath, stdin_string))
    else:
        g.note("Skipped writing the stdin buffer.")
