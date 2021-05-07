import pyeda.inter



vartuple = tuple(map(pyeda.inter.exprvar, "abcdefghijkl"))

def bin2var(b, v):
    return v if b == "1" else (~v)

def andprod(l):
    ret = l[0]
    for v in l[1:]:
        ret &= v
    return ret

def orsum(l):
    ret = l[0]
    for v in l[1:]:
        ret |= v
    return ret

def espresso2litlist_list(l):
    if l[0] != "or":
        l = ("or", l)
    ret = []
    for l1 in l[1:]:
        try:
            ret.append(tuple([l2[1] for l2 in l1[1:]]))
        except Exception as e:
            print(l1)
            print(l1[1:])
            raise(e)
    return tuple(ret)

def litlist2str(l , bitlength=12):
    ret = ""
    for i in range(1,bitlength+1):
        if not (i in l or -i in l):
            addstr = "-"
        elif i in l:
            addstr = "1"
        else:
            addstr = "0"
        ret = ret + addstr
    return ret


def minimize_binlist(binlist):
    f1 = orsum([andprod([bin2var(*t) for t in zip(binary, vartuple)]) for binary in binlist])

    f1m, = pyeda.inter.espresso_exprs(f1.to_dnf())
    # print(f1m)

    ast = f1m.to_ast()
    litlist_list = espresso2litlist_list(ast)
    minimized = tuple([litlist2str(l, bitlength=12) for l in litlist_list])
    return minimized

if __name__ == "__main__":
    binlist = [
        "000",
        "001",
        "101",
        "111",
        "110"
    ]


    print(minimize_binlist(binlist))