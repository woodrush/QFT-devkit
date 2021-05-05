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


# calc.c
RAM_NEGATIVE_BUFFER_SIZE = 200
QFTASM_RAMSTDIN_BUF_STARTPOSITION = 700 + RAM_NEGATIVE_BUFFER_SIZE
QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 1100 + RAM_NEGATIVE_BUFFER_SIZE




# p_init = (425, 239)
# p_init = (346+16*2, 239)
# p_init = (409, 239)
# p_init = (353, 239)
# p_init = (329, 239)
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

def write_byte_at(write_byte, addr):
    if addr < 11:
        addr = addr
    if addr > 32768:
        addr = 32768 - addr + 11
    if addr >= 11:
        addr = addr + RAM_NEGATIVE_BUFFER_SIZE
    b_binary = "{:016b}".format(write_byte)
    for i_bit, bit in enumerate(b_binary):
        for x_offset in range(2):
            g.setcell(p_init[0] + i_bit * delta_x + x_offset, p_init[1] + addr * delta_y, d_bit2state[int(bit)])

def write_ram(stdin_string):
    stdin_bytes = encode_stdin_string(stdin_string)
    # g.note("Raw stdin bytes:" + str(stdin_bytes))
    for i_byte, b in enumerate(stdin_bytes):
        write_byte_at(b, i_byte + QFTASM_RAMSTDIN_BUF_STARTPOSITION - RAM_NEGATIVE_BUFFER_SIZE)

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











write_bytes = [
    (1400,1),
    (1100,2),
    (108,11),
    (97,12),
    (109,13),
    (98,14),
    (100,15),
    (97,16),
    (112,18),
    (114,19),
    (105,20),
    (110,21),
    (116,22),
    (100,24),
    (101,25),
    (102,26),
    (105,27),
    (110,28),
    (101,29),
    (113,31),
    (117,32),
    (111,33),
    (116,34),
    (101,35),
    (108,37),
    (105,38),
    (115,39),
    (116,40),
    (105,42),
    (102,43),
    (99,45),
    (97,46),
    (114,47),
    (119,49),
    (104,50),
    (105,51),
    (108,52),
    (101,53),
    (112,55),
    (114,56),
    (111,57),
    (103,58),
    (110,59),
    (109,61),
    (97,62),
    (99,63),
    (114,64),
    (111,65),
    (108,67),
    (97,68),
    (109,69),
    (98,70),
    (100,71),
    (97,72),
    (42,73),
    (101,75),
    (113,76),
    (99,78),
    (111,79),
    (110,80),
    (115,81),
    (43,83),
    (116,85),
    (109,87),
    (111,88),
    (100,89),
    (101,91),
    (118,92),
    (97,93),
    (108,94),
    (99,96),
    (100,97),
    (114,98),
    (45,100),
    (42,102),
    (60,104),
    (62,106),
    (47,108),
    (97,110),
    (116,111),
    (111,112),
    (109,113),
    (1742,115),
    (1620,119),
    (1312,122),
    (2301,125),
    (286,127),
    (1476,128),
    (1387,131),
    (1426,132),
    (1698,134),
    (1660,137),
    (1742,140),
    (1742,143),
    (1830,147),
    (290,148),
    (1577,149),
    (290,150),
    (1893,151),
    (290,152),
    (1893,153),
    (2373,155),
    (1452,158),
    (1893,160),
    (1893,161),
    (2153,162),
    (2153,163),
    (1893,164),
    (2311,165),
    (108,198),
    (42,201),
    (198,202),
    (106,204),
    (31,207),
    (204,208),
    (100,210),
    (18,213),
    (210,214),
    (104,216),
    (37,219),
    (216,220),
    (67,222),
    (83,225),
    (24,228),
    (225,229),
    (222,230),
    (102,231),
    (49,234),
    (96,237),
    (234,239),
    (91,240),
    (55,243),
    (45,246),
    (75,249),
    (246,250),
    (243,251),
    (85,252),
    (78,255),
    (61,258),
    (110,261),
    (11,264),
    (261,265),
    (87,267),
    (267,270),
    (264,271),
    (258,272),
    (255,273),
    (252,274),
    (249,276),
    (240,278),
    (237,279),
    (231,280),
    (228,281),
    (219,282),
    (213,283),
    (207,284),
    (201,285),
    (1,287),
    (76,294),
    (97,295),
    (109,296),
    (98,297),
    (100,298),
    (97,299),
    (62,300),
    (77,302),
    (97,303),
    (99,304),
    (114,305),
    (111,306),
    (62,307),
    (67,309),
    (108,310),
    (111,311),
    (115,312),
    (117,313),
    (114,314),
    (101,315),
    (62,316),
    (319,318),
]


# g.show("Writing bytes...")
# for content, addr in write_bytes:
#     write_byte_at(content, addr)
# g.show("Done.")













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

# write_ram_string = "(print (* 3 14))"

# write_ram_string = "3*2+1"

# write_ram_string = ""

if len(write_ram_string) > 0:
    write_ram(write_ram_string)

show_stdio()


