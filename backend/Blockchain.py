import time
from Block import Block


class Blockchain:
    def __init__(self):
        self.unconfirmedTransactions = []
        self.chain = []
        self.difficulty = 2
        self.createGenesisBlock()

    def createGenesisBlock(self):
        genesisBlock = Block(0, [], time.time(), "0")
        genesisBlock.hash = genesisBlock.computeHash()
        self.chain.append(genesisBlock)

    @property
    def lastBlock(self):
        return self.chain[-1]

    def proofOfWork(self, block):
        block.nonce = 0
        computedHash = block.computeHash()
        while not computedHash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computedHash = block.computeHash
        return computedHash

    def addBlock(self, block, proof):
        previousHash = self.lastBlock.hash
        if previousHash != block.previousHash:
            return False
        if not Blockchain.isValidProof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def isValidProof(self, block, blockHash):
        return ((blockHash.startswith('0') * Blockchain.difficulty) and blockHash == block.computeHash())

    def addNewTransactions(self, transactions):
        self.unconfirmedTransactions.append(transactions)

    def mine(self):
        if not self.unconfirmedTransactions:
            return False

        lastBlock = self.lastBlock
        newBlock = Block(idx=lastBlock.idx + 1,
                         transactions=self.unconfirmedTransactions,
                         timestamp=time.time(),
                         previousHash=lastBlock.hash)
        proof = self.proofOfWork(newBlock)
        self.addBlock(newBlock, proof)
        self.unconfirmedTransactions = []
        return newBlock.idx
