import random

from datetime import datetime
def crate_random_code(len_code):
    b = 0
    code_crated = ''
    while b < int(len_code):
        code_crated += str(random.randint(0, 9))
        b += 1
    return code_crated


def create_random_name(lent: int):
    list_str = ['a', '1', '2', 'q', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', 'a', 's', 'd', 'f', 'g',
                'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', '4', '4', 'n', '2', '7', 'n', 'm', '0', '1', '2',
                '3', '4', '5', '6', '7', '8', '9', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'S',
                'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M']
    name = ''
    b = 1
    while b <= lent:
        name += list_str[random.randint(0, len(list_str) - 1)]
        b += 1
    return name


def convert_timestamp(timestamp):
    # تبدیل Timestamp به datetime
    dt_object = datetime.utcfromtimestamp(int(timestamp))
    return dt_object



def change_file_name(file_name, new_file_name):
    find = False
    b = 0
    ft = ''
    o_name = ''
    while b < len(file_name):
        if find:
            ft += file_name[b]
        elif file_name[b] == '.':
            find = True
        else:
            o_name += file_name[b]
        b += 1
    return f'{o_name}{new_file_name}.{ft}'
