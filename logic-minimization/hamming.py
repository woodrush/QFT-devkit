from pyparsing import *
import sys
from graphviz import Graph
from lm import minimize_binlist
import matplotlib.pyplot as plt

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

with open("./rom.qftasm", "rt") as f:
    rawcode = f.read()

parser = Parser()
parsed = parser.parse_string(rawcode)


def rev(s):
    return "".join(reversed(s))

d = {}


for line in parsed:
    lineno, opcode, (d_1, n_1), (d_2, n_2), (d_3, n_3) = line
    inst = opcode, (d_1, n_1), (d_2, n_2), (d_3, n_3)

    # inst = opcode, (d_1, n_1)
    # inst = (d_2, n_2)
    # inst = (d_3, n_3)
    if inst not in d.keys():
        d[inst] = []
    d[inst].append(lineno)

vlenlist = []
print("Original:", len(parsed))
print("Distinct instructions:", len(d.keys()))
# print(tuple(d.keys()))
vlenlist = [len(v) for _, v in d.items()]

plt.figure()
plt.plot(sorted(vlenlist, reverse=True), "-o")
plt.savefig("instlen.png")

optsum = 0

optlenlist = []
for k in d.keys():
    instlines = d[k]
    if len(instlines) <= 1:
        optsum += 1
        continue
    binlist = ["".join(reversed("{:012b}".format(x))) for x in instlines]
    minimized = minimize_binlist(binlist)

    optsum += len(minimized)
    if len(binlist) > len(minimized):
        print("{} -> {}".format(len(binlist), len(minimized)))
        optlenlist.append(len(binlist) - len(minimized))

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
