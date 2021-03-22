from typing import List


class CouriersLoadException(Exception):
    def __init__(self, ids: List[int] = []):
        self.ids = ids
