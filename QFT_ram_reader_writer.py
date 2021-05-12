import golly as g

# QFTASM_RAMSTDIN_BUF_STARTPOSITION = 7291
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 8191

# QFTASM_RAMSTDIN_BUF_STARTPOSITION = 4607
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 5119

# QFTASM_RAMSTDIN_BUF_STARTPOSITION = 4499
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 4999

# QFTASM_RAMSTDIN_BUF_STARTPOSITION = 503
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 511

# QFTASM_RAMSTDIN_BUF_STARTPOSITION = 4095-1024-512
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 4095-1024-(512-128)



# # calc.c
# RAM_NEGATIVE_BUFFER_SIZE = 50
# QFTASM_RAMSTDIN_BUF_STARTPOSITION = 61 + RAM_NEGATIVE_BUFFER_SIZE
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 63 + RAM_NEGATIVE_BUFFER_SIZE

# # calc.c
# RAM_NEGATIVE_BUFFER_SIZE = 200
# QFTASM_RAMSTDIN_BUF_STARTPOSITION = 688 + RAM_NEGATIVE_BUFFER_SIZE
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 1200 + RAM_NEGATIVE_BUFFER_SIZE

# # lisp.c
# RAM_NEGATIVE_BUFFER_SIZE = 500
# QFTASM_RAMSTDIN_BUF_STARTPOSITION = (4095-1024-512) + RAM_NEGATIVE_BUFFER_SIZE
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = (4095-1024-(512-128)) + RAM_NEGATIVE_BUFFER_SIZE

# # calc.c
# RAM_NEGATIVE_BUFFER_SIZE = 200
# QFTASM_RAMSTDIN_BUF_STARTPOSITION = 688 + RAM_NEGATIVE_BUFFER_SIZE
# QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 1200 + RAM_NEGATIVE_BUFFER_SIZE

s1 = g.getstring("Enter stack size:", "233")
s2 = g.getstring("Enter stdin buffer starting address:", "290")
s3 = g.getstring("Enter stdout buffer starting address:", "790")

# calc.c
RAM_NEGATIVE_BUFFER_SIZE = int(s1)
QFTASM_RAMSTDIN_BUF_STARTPOSITION = int(s2) + RAM_NEGATIVE_BUFFER_SIZE
QFTASM_RAMSTDOUT_BUF_STARTPOSITION = int(s3) + RAM_NEGATIVE_BUFFER_SIZE

RAM_SIZE = 1024


# p_init = (425, 239)
# p_init = (346+16*2, 239)
# p_init = (409, 239)
# p_init = (353, 239)
# p_init = (329, 239)
# p_init = (321, 239)
# p_init = (329, 239)

# p_init = (289, 239)
p_init = (337, 239)

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
    0: 6,
    1: 7,
}

def write_byte_at(addr, write_byte):
    if addr < 11:
        addr = addr
    # elif addr > 32768:
    #     addr = 32768 - addr + 11
    elif addr >= RAM_SIZE - RAM_NEGATIVE_BUFFER_SIZE:
        addr = RAM_SIZE - addr + 10
    elif addr >= 11:
        addr = addr + RAM_NEGATIVE_BUFFER_SIZE
    b_binary = "{:016b}".format(write_byte)
    for i_bit, bit in enumerate(b_binary):
        for x_offset in range(2):
            g.setcell(p_init[0] + i_bit * delta_x + x_offset, p_init[1] + addr * delta_y, d_bit2state[int(bit)])

def write_ram(stdin_string):
    stdin_bytes = encode_stdin_string(stdin_string)
    # g.note("Raw stdin bytes:" + str(stdin_bytes))
    for i_byte, b in enumerate(stdin_bytes):
        write_byte_at(i_byte + QFTASM_RAMSTDIN_BUF_STARTPOSITION - RAM_NEGATIVE_BUFFER_SIZE, b)

def show_stdio():
    d_state2bit = {
        6: 0,
        7: 1,
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



write_bytes_filepath = g.opendialog("Open CSV for the Initial RAM Values", "CSV files (*.csv)|*.csv")

if write_bytes_filepath:
    with open(write_bytes_filepath, "rt") as f:
        write_bytes = [map(int, line.split(",")) for line in f.readlines()]

    g.show("Writing initial RAM bytes...")
    for t in write_bytes:
        write_byte_at(*t)
    g.show("Done.")
    g.note("Written {} initial RAM bytes.".format(len(write_bytes)))
else:
    g.note("Skipped writing initial RAM bytes.")




show_raw_ram_region()

show_registers()

write_ram_string = ""


# write_ram_string = g.getstring("Enter string to write to stdin (blank for not writing):")


write_ram_string = """(define defun
  (macro (fname varlist body)
    (list
      (quote define) fname
      (list (quote lambda*) varlist body))))

(defun append (l item)
  (if l
    (cons (car l) (append (cdr l) item))
    (cons item ())))

(defun isprime (n)
  ((lambda* (primelist p ret)
     (progn
       (while primelist
         (progn
           (define p (car primelist))
           (define primelist (cdr primelist))
           (if (eq 0 (mod n p))
             (progn
               (define primelist ())
               (define ret ()))
             ())))
       ret))
   primelist () 1))

(define n 2)
(define nmax 20)
(define primelist (cons 2 ()))

(while (< n nmax)
  (progn
    (define n (+ 1 n))
    (if (isprime n)
      (define primelist (append primelist n))
      ())))

(print primelist)"""

# write_ram_string = """(print
#   (((lambda (f)
#       ((lambda (x) (f (lambda (v) ((x x) v))))
#        (lambda (x) (f (lambda (v) ((x x) v))))))
#     (lambda (fact)
#       (lambda (n)
#         (if (eq n 0) 1 (* n (fact (- n 1)))))))
#    5))"""

# write_ram_string = """(define counter
#   (lambda (n)
#     (lambda (methodname)
#       (if (eq methodname (quote inc))
#         (lambda () (define n (+ n 1)))
#       (if (eq methodname (quote dec))
#         (lambda () (define n (- n 1)))
#       (if (eq methodname (quote get))
#         (lambda () n)
#       (if (eq methodname (quote set))
#         (lambda (m) (define n m))
#         ())))))))

# (define . (macro (object methodname) (list object (list (quote quote) methodname))))
# (define new (lambda (x) (x)))

# (define counter1 (new counter))
# (define counter2 (new counter))

# ((. counter1 set) 0)
# ((. counter2 set) 8)

# (print ((. counter1 inc)) ())
# (print ((. counter1 inc)) ())
# (print ((. counter1 inc)) ())
# (print ((. counter2 inc)) ())
# (print ((. counter2 dec)) ())
# (print ((. counter1 inc)) ())
# (print ((. counter2 inc)) ())"""

write_ram_string = "(print (* 3 14))"

# write_ram_string = "3*2+1"

# write_ram_string = ""

write_ram_string = g.getstring("Enter string to write to the RAM: (blank for not writing)", write_ram_string)

if len(write_ram_string) > 0:
    write_ram(write_ram_string)

show_stdio()


