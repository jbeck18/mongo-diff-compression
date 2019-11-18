a = {
    'a': {
        'b': 0,
        'c': 1,
        'd': 2
    },
    'e': {
        'f': {
            'g': {
                'h': 3,
                'i': 4
            },
            'j': 5,
            'k': 6
        }
    },
    'l': [0,1,2]
}

b = {
    'a': {
        'b': 0,
        'c': 10,
        'd': 2
    },
    'e': {
        'f': {
            'g': {
                'h': 30,
                'i': 4
            },
            'j': 5,
            'k': 60
        }
    },
    'l': [0,1,2]
}

def compute(before: dict, after: dict, diff, path=None):
    for key in after:
        old_val, new_val = before.get(key), after.get(key)

        if old_val == new_val:
            continue

        if type(old_val) is dict and type(new_val) is dict:
            if path:
                newPath = f'{path}.{key}'
            else:
                newPath = key

            compute(old_val, new_val, path=newPath, diff=diff)
            continue
            
        if not path:
            diff[key] = old_val
        else:
            diff[f'{path}.{key}'] = new_val

res = {}
compute(a, b, res)
print(res)