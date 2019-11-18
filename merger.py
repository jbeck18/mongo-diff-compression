class Merger:
    
    def merge_changes_list(self, current: list, changes: list):
        indices_to_remove = []
        for entry in changes:
            index, diff = entry['index'], entry['diff']

            if type(diff) is list and index < len(current) and type(current[index]) is list:
                self.merge_changes_list(current[index], diff)
            elif type(diff) is dict and index < len(current) and type(current[index]) is dict:
                self.merge_changes(current[index], diff)
            else:
                if index == len(current):
                    current.append(diff)
                else:
                    if diff is None:
                        indices_to_remove.append(index)
                    else:
                        current[index] = diff

        for index in indices_to_remove[::-1]:
            del current[index]

    def merge_changes(self, current: dict, changes: dict):
        for key in list(changes):
            if changes[key] is None:
                del current[key]
            elif type(changes[key]) is dict and type(current.get(key)) is dict:
                self.merge_changes(current[key], changes[key])
            elif type(current.get(key)) is list and type(changes.get(key)) is list:
                self.merge_changes_list(current[key], changes[key])
            else:
                current[key] = changes[key]