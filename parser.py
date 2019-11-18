import typing
import bson
import datetime

from typing import List, Dict

# All bson scalar types
BSON_SCALAR = typing.Union[
    bytes,
    bool,
    bson.code.Code,
    datetime.datetime,
    bson.decimal128.Decimal128,
    float,
    int,
    bson.int64.Int64,
    bson.objectid.ObjectId,
    bson.regex.Regex,
    str,
    bson.timestamp.Timestamp
]

# Final bson type union
BSON = typing.Union[
    BSON_SCALAR,
    List['BSON'],
    Dict[str, 'BSON']
]

class Parser:

    def parse(self, before: BSON, after: BSON):
        """Computes the diff between the `before` and `after` parameters
        
        Arguments:
            before {str} -- The previous state of the document
            after {BSON} -- The current state of the document
        """
        res = {}
        self._compute_diff_dict(before, after, res)
        return res

    def _compute_diff(self, before: BSON, after: BSON, key: str, diff: dict, path=None):
        """Computes the diff between two BSON types
        
        Arguments:
            before {BSON} -- The previous state of the BSON
            after {BSON} -- The current state of the BSON
            key {str} -- The key associated with the current value
            diff {dict} -- A dict storing the differences in each BSON document
        
        Keyword Arguments:
            path {[type]} -- The path to the current place in the scan.
                             Uses mongo convention. E.g. `key.nested_key` (default: {None})
        """
        if before == after:
            return

        if type(before) is dict and type(after) is dict:
            self._compute_diff_dict(before, after, diff, path=path)
            return
            
        if type(before) is list and type(after) is list:
            self._compute_diff_list(before, after, key, diff, path=path)
            return

        self._compute_diff_scalar(before, after, diff, key, path=path)

    def _compute_diff_dict(self, before: Dict[str, BSON], after: Dict[str, BSON], diff, path=None):
        """Computes the diff between two bson dicts
        
        Arguments:
            before {Dict[str, BSON]} -- The previous state of the BSON dict
            after {Dict[str, BSON]} -- The current state of the BSON dict
            diff {[type]} -- A dict storing the differences in each BSON document
        
        Keyword Arguments:
            path {[type]} -- The path to the current place in the scan.
                             Uses mongo convention. E.g. `key.nested_key` (default: {None})
        """
        if before == after:
            return

        for key in before.keys() | after.keys():
            old_val, new_val = before.get(key), after.get(key)

            new_path = f'{path}.{key}' if path else key
            self._compute_diff(old_val, new_val, key, diff, path=new_path)

    def _compute_diff_list(self, before: List[BSON], after: List[BSON], key, diff: dict, path=None):
        """Computes the diff between two bson lists
        
        Arguments:
            before {List[BSON]} -- The previous state of the BSON list
            after {List[BSON]} -- The current state of the BSON list
            key {[type]} -- The current key being used in the scan
            diff {dict} -- A dict storing the differences in each BSON document
        
        Keyword Arguments:
            path {[type]} -- The path to the current place in the scan.
                             Uses mongo convention. E.g. `key.nested_key` (default: {None})
        """
        if before == after:
            return

        max_length = max(len(before), len(after))
        res = []

        for i in range(max_length):
            old = before[i] if i < len(before) else None
            new = after[i] if i < len(after) else None

            elem_diff = {}
            self._compute_diff(old, new, key, elem_diff, path=None)
            if not elem_diff:
                continue

            obj = {
                'index': i,
                'diff': elem_diff[key] if key in elem_diff else elem_diff
            }
            res.append(obj)


        self._goto_path(diff, path)[key] = res

    def _compute_diff_scalar(self, before: BSON_SCALAR, after: BSON_SCALAR, diff: dict, key, path=None):
        """Stores the changes for a scalar in the diff
        
        Arguments:
            before {BSON_SCALAR} -- The previous value of the BSON scalar
            after {BSON_SCALAR} -- The current value of the BSON scalar
            diff {dict} -- [description]
            key {[type]} -- [description]
        
        Keyword Arguments:
            path {[type]} -- The path to the current place in the scan.
                             Uses mongo convention. E.g. `key.nested_key` (default: {None})
        """
        if before == after:
            return

        self._goto_path(diff, path)[key] = before

    def _goto_path(self, diff: dict, path: str):
        if not path:
            return diff

        parts = path.split('.')[:-1]
        node = diff
        for part in parts:
            if part not in node:
                node[part] = {}

            node = node[part]

        return node

