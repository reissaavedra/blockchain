import json
from hashlib import sha256


class Block:
    def __init__(self, idx, transactions, timestamp, previousHash):
        self.idx = idx
        self.transactions = transactions
        self.timestamp = timestamp
        self.previousHash = previousHash

    def computeHash(self):
        blockString = json.dumps(self.__dict__, sort_keys=True)
        return sha256(blockString.encode()).hexdigest()