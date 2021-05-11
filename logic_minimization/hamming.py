from pyparsing import *
import sys
from logic_minimization.lm import minimize_binlist

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


def rev(s):
    return "".join(reversed(s))

# d = {}


# for line in parsed:
#     lineno, opcode, (d_1, n_1), (d_2, n_2), (d_3, n_3) = line
#     inst = opcode, (d_1, n_1), (d_2, n_2), (d_3, n_3)

#     # inst = opcode, (d_1, n_1)
#     # inst = (d_2, n_2)
#     # inst = (d_3, n_3)
#     if inst not in d.keys():
#         d[inst] = []
#     d[inst].append(lineno)

# vlenlist = []
# print("Original:", len(parsed))
# print("Distinct instructions:", len(d.keys()))
# # print(tuple(d.keys()))
# vlenlist = [len(v) for _, v in d.items()]

# plt.figure()
# plt.plot(sorted(vlenlist, reverse=True), "-o")
# plt.savefig("instlen.png")

def get_minimized_rom(d_insthash2lineno):
    # import golly as g

    ret = []

    optsum = 0

    optlenlist = []
    grandlist = []
    # g.note("Hi!")
    for k, instlines in d_insthash2lineno.items():
        # instlines = d_insthash2lineno[k]
        if len(instlines) == 1:
            # binstring = "".join(reversed("{:012b}".format(instlines[0])))
            binstring = "".join("{:012b}".format(instlines[0]))
            ret += [(binstring, k)]
            continue
        elif len(instlines) < 1:
            optsum += 1
            continue
        # binlist = ["".join(reversed("{:012b}".format(x))) for x in instlines]
        binlist = ["".join("{:012b}".format(x)) for x in instlines]
        minimized = minimize_binlist(binlist)
        # print(binlist)
        grandlist += minimized
        print(minimized)

        optsum += len(minimized)
        if len(binlist) > len(minimized):
            print("{} -> {}".format(len(binlist), len(minimized)))
            optlenlist.append(len(binlist) - len(minimized))
        
        ret += [(x, k) for x in minimized]

    return ret, optlenlist, optsum


if __name__ == "__main__":
    from graphviz import Graph
    import matplotlib.pyplot as plt

    with open("./rom.qftasm", "rt") as f:
        rawcode = f.read()

    parser = Parser()
    parsed = parser.parse_string(rawcode)

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

    d_insthash2lineno = {}
    for lineno, insthash in l_binstring_pc2hash:
        # insthash = insthash[5:]
        if insthash not in d_insthash2lineno.keys():
            d_insthash2lineno[insthash] = []
        d_insthash2lineno[insthash].append(lineno)

    # optsum = 0

    # optlenlist = []
    # grandlist = []
    # for k in d_insthash2lineno.keys():
    #     instlines = d_insthash2lineno[k]
    #     if len(instlines) <= 1:
    #         optsum += 1
    #         continue
    #     binlist = ["".join(reversed("{:012b}".format(x))) for x in instlines]
    #     minimized = minimize_binlist(binlist)
    #     # print(binlist)
    #     grandlist += minimized
    #     print(minimized)

    #     optsum += len(minimized)
    #     if len(binlist) > len(minimized):
    #         print("{} -> {}".format(len(binlist), len(minimized)))
    #         optlenlist.append(len(binlist) - len(minimized))

    _, optlenlist, optsum = get_minimized_rom(d_insthash2lineno)

    print(len(parsed))
    print(optsum)

    plt.figure()
    plt.plot(sorted(optlenlist, reverse=True), "-o")
    plt.savefig("optlen.png")


    # def setgraph(g):
    #     for i_a, a in enumerate(zerolines):
    #         # g.node(str(a))
    #         for i_b, b in enumerate(zerolines):
    #             if i_b <= i_a:
    #                 continue
    #             if sum([int(c) for c in "{:b}".format(a ^ b)]) == 2:
    #                 print(a, b, "{:b}".format(a), "{:b}".format(b))
    #                 g.edge(str(a), str(b))
    #                 # g.edge(str(b), str(a))
    # # print(zerolines)

    # # # Sorting: 392kb
    # # l_binstring = sorted(l_binstring, key=lambda x: x[1], reverse=True)


    # g = Graph(format="pdf")
    # setgraph(g)
    # g.render("hamminggraph")
