import string
import random

def gen_token():
    return ''.join(
        random.choice(string.ascii_letters+string.digits) for x in range(15)
    )
