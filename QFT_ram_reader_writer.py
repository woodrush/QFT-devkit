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
QFTASM_RAMSTDIN_BUF_STARTPOSITION = 350 + RAM_NEGATIVE_BUFFER_SIZE
QFTASM_RAMSTDOUT_BUF_STARTPOSITION = 823 + RAM_NEGATIVE_BUFFER_SIZE




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
    elif addr >= 1024 - RAM_NEGATIVE_BUFFER_SIZE:
        addr = 1024 - addr + 10
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











write_bytes = [
    # precalculated_memmap.txt
    (856,65385),
    (857,65391),
    (858,65394),
    (859,65397),
    (860,65400),
    (861,0),
    (862,65409),
    (863,0),
    (864,65412),
    (865,65418),
    (866,65421),
    (867,65430),
    (868,65436),
    (869,65442),
    (870,65448),
    (871,65451),
    (872,65454),
    (873,87),
    (874,0),
    (875,0),
    (876,110),
    (877,0),
    (878,0),
    (879,11),
    (880,65388),
    (881,0),
    (882,61),
    (883,0),
    (884,0),
    (885,78),
    (886,0),
    (887,0),
    (888,85),
    (889,0),
    (890,0),
    (891,55),
    (892,0),
    (893,0),
    (894,45),
    (895,0),
    (896,0),
    (897,75),
    (898,65406),
    (899,65403),
    (900,91),
    (901,0),
    (902,0),
    (903,49),
    (904,0),
    (905,0),
    (906,96),
    (907,0),
    (908,65415),
    (909,102),
    (910,0),
    (911,0),
    (912,67),
    (913,0),
    (914,0),
    (915,83),
    (916,0),
    (917,0),
    (918,24),
    (919,65427),
    (920,65424),
    (921,104),
    (922,0),
    (923,0),
    (924,37),
    (925,65433),
    (926,0),
    (927,100),
    (928,0),
    (929,0),
    (930,18),
    (931,65439),
    (932,0),
    (933,106),
    (934,0),
    (935,0),
    (936,31),
    (937,65445),
    (938,0),
    (939,42),

    # Memory initialization
    (1,700),
    (2,823),
    (11,108),
    (12,97),
    (13,109),
    (14,98),
    (15,100),
    (16,97),
    (18,112),
    (19,114),
    (20,105),
    (21,110),
    (22,116),
    (24,100),
    (25,101),
    (26,102),
    (27,105),
    (28,110),
    (29,101),
    (31,113),
    (32,117),
    (33,111),
    (34,116),
    (35,101),
    (37,108),
    (38,105),
    (39,115),
    (40,116),
    (42,105),
    (43,102),
    (45,99),
    (46,97),
    (47,114),
    (49,119),
    (50,104),
    (51,105),
    (52,108),
    (53,101),
    (55,112),
    (56,114),
    (57,111),
    (58,103),
    (59,110),
    (61,109),
    (62,97),
    (63,99),
    (64,114),
    (65,111),
    (67,108),
    (68,97),
    (69,109),
    (70,98),
    (71,100),
    (72,97),
    (73,42),
    (75,101),
    (76,113),
    (78,99),
    (79,111),
    (80,110),
    (81,115),
    (83,43),
    (85,116),
    (87,109),
    (88,111),
    (89,100),
    (91,101),
    (92,118),
    (93,97),
    (94,108),
    (96,99),
    (97,100),
    (98,114),
    (100,45),
    (102,42),
    (104,60),
    (106,62),
    (108,47),
    (110,97),
    (111,116),
    (112,111),
    (113,109),
    (115,1787),
    (119,1665),
    (122,1357),
    (125,2349),
    (127,168),
    (128,1521),
    (131,1432),
    (132,1471),
    (134,1743),
    (137,1705),
    (140,1787),
    (143,1787),
    (147,1878),
    (148,156),
    (149,1622),
    (150,156),
    (151,1941),
    (152,156),
    (153,1941),
    (155,2421),
    (158,1497),
    (160,1941),
    (161,1941),
    (162,2201),
    (163,2201),
    (164,1941),
    (165,2359),
    (166,350),
    (167,65384),
    (169,1),
    (172,16469),
    (175,76),
    (176,97),
    (177,109),
    (178,98),
    (179,100),
    (180,97),
    (181,62),
    (183,77),
    (184,97),
    (185,99),
    (186,114),
    (187,111),
    (188,62),
    (190,67),
    (191,108),
    (192,111),
    (193,115),
    (194,117),
    (195,114),
    (196,101),
    (197,62),
    (199,200),
]


g.show("Writing bytes...")
for t in write_bytes:
    write_byte_at(*t)
g.show("Done.")













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

if len(write_ram_string) > 0:
    write_ram(write_ram_string)

show_stdio()


