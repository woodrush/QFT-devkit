import golly as g

# QFTASM_RAMSTDIN_BUF_STARTPOSITION = 7291
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 8191

# QFTASM_RAMSTDIN_BUF_STARTPOSITION = 4607
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 5119

# QFTASM_RAMSTDIN_BUF_STARTPOSITION = 4499
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 4999

QFTASM_RAMSTDIN_BUF_STARTPOSITION = 503
QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 511

p_init = (425, 239)

delta_x = 16
delta_y = 16

def getcell_by_index(i_x, i_y):
    return g.getcell(p_init[0] + i_x * delta_x, p_init[1] + i_y * delta_y)

def get_rambyte_by_addr_str(addr):
    bytestring = "".join([str(getcell_by_index(i_x, addr) - 6) for i_x in range(16)])
    return bytestring

def get_rambyte_by_addr_int(addr):
    return int(get_rambyte_by_addr_str(addr), 2)

def show_raw_ram_region(i_x0=0, i_y0=0, i_x1=15, i_y1=32, reverse=False):
    def cell2chr(c):
        d = {6:"_", 7:"*"}
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

def write_ram(stdin_string):
    d_bit2state = {
        0: 6,
        1: 7,
    }
    stdin_bytes = [ord(c) for c in stdin_string]
    for i_byte, b in enumerate(stdin_bytes):
        b_binary = "{:016b}".format(b)
        for i_bit, bit in enumerate(b_binary):
            for x_offset in range(2):
                g.setcell(p_init[0] + i_bit * delta_x + x_offset, p_init[1] + (QFTASM_RAMSTDIN_BUF_STARTPOSITION - i_byte) * delta_y, d_bit2state[int(bit)])

def show_stdio():
    d_state2bit = {
        6: 0,
        7: 1,
    }
    stdin_bitstr = ["".join([str(d_state2bit[getcell_by_index(i_x, i_y)]) for i_x in range(16)])
        for i_y in range(QFTASM_RAMSTDIN_BUF_STARTPOSITION, 0, -1)
    ]
    stdin_bytes = [int(s,2) for s in stdin_bitstr]
    stdin_str = ""
    for c in stdin_bytes:
        if c == 0:
            break
        stdin_str += chr(c)

    stdout_bitstr = ["".join([str(d_state2bit[getcell_by_index(i_x, i_y)]) for i_x in range(16)])
        for i_y in range(QFTASM_RAMSTDOUT_BUF_STARTPOSITION, QFTASM_RAMSTDIN_BUF_STARTPOSITION, -1)
    ]
    stdout_bytes = [int(s,2) for s in stdout_bitstr]
    stdout_str = "".join([chr(c) for c in stdout_bytes if c != 0])

    g.note("Stdin:\n" + stdin_str + "\n\nStdout:\n" + stdout_str)


show_raw_ram_region()

show_registers()

write_ram_string = ""

# write_ram_string = g.getstring("Enter string to write to stdin (blank for not writing):")

# write_ram_string = "(print (* 3 14))"

# write_ram_string = """(define defun
#   (macro (fname varlist body)
#     (cons (quote define)
#     (cons fname
#     (cons (cons (quote lambda)
#           (cons varlist
#           (cons body ()))) ())))))

# (defun append (l item)
#   (if l
#     (cons (car l) (append (cdr l) item))
#     (cons item ())))

# (defun isprime (n)
#   ((lambda (primelist p ret)
#      (progn
#        (while primelist
#          (progn
#            (define p (car primelist))
#            (define primelist (cdr primelist))
#            (if (eq 0 (mod n p))
#              (progn
#                (define primelist ())
#                (define ret ()))
#              ())))
#        ret))
#    primelist () 1))

# (define n 2)
# (define nmax 20)
# (define primelist (cons 2 ()))

# (while (< n nmax)
#   (progn
#     (define n (+ 1 n))
#     (if (isprime n)
#       (define primelist (append primelist n))
#       ())))

# (print primelist)"""


if len(write_ram_string) > 0:
    write_ram(write_ram_string)

show_stdio()
