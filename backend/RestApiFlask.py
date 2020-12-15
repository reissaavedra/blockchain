from flask import Flask, request
import requests
import time
import json

from Block import Block
from Blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()


@app.route('/newTransaction', methods=['POST'])
def newTransaction():
    txData = request.get_json()
    requiredFields = ['author', 'content']
    for field in requiredFields:
        if not txData.get(field):
            return 'Invalid transaction data', 404

    txData['timestamp'] = time.time()
    blockchain.addNewTransactions(txData)
    return 'Success', 201


@app.route('/chain', methods=['GET'])
def getChain():
    chainData = []
    for block in blockchain.chain:
        chainData.append(block.__dict__)
    return json.dumps({
        'length': len(chainData),
        'chain': chainData
    })


# @app.route('/mine', methods=['GET'])
# def mineUnconfirmedTransactions():
#     result = blockchain.mine()
#     if not result:
#         return 'No transactions to mine'
#     return 'Block #{} is mined.'.format(result)


@app.route('/pendingTx')
def getPendingTx():
    return json.dumps(blockchain.unconfirmedTransactions)


# Establishing P2P(Peer to peer) connection
peers = set()


@app.route('/registerNode', methods=['POST'])
def registerNewPeers():
    nodeAddress = request.get_json()['nodeAddress']
    if not nodeAddress:
        return 'Invalid data', 400

    peers.add(nodeAddress)
    return getChain()


@app.route('/registerWith', methods=['POST'])
def registerWithExistingNode():
    nodeAddress = request.get_json()['nodeAddress']
    if not nodeAddress:
        return 'Invalid data 2', 400

    data = {'nodeAddress': request.host_url}
    headers = {'Content-Type': 'application/json'}

    response = request.post(nodeAddress + '/registerNode',
                            data=json.dumps(data),
                            headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers

        chainDump = response.json()['chain']
        blockchain = createChainFromDump(chainDump)
        peers.update(response.json()['peers'])
        return 'Registration Succesful', 200
    else:
        return response.content, response.status_code


def createChainFromDump(chainDump):
    blockchain = Blockchain()
    for idx, blockData in enumerate(chainDump):
        block = Block(blockData['idx'],
                      blockData['transactions'],
                      blockData['timestamp'],
                      blockData['previousHash'])
        proof = blockData['hash']

        if idx > 0:
            added = blockchain.addBlock(block, proof)
            if not added:
                raise Exception('The chain dump is tempered!!!!!!!!!')
        else:
            blockchain.chain.append(block)
    return blockchain


def checkChainValidity(cls, chain):
    result = True
    previousHash = '0'

    for block in chain:
        blockHash = block.hash
        delattr(block, 'hash')

        if not cls.isValidProof(block, block.hash) or previousHash != block.previousHash:
            return False
            break

        block.hash, previousHash = blockHash, blockHash

    return result


def consensus():
    global blockchain
    longestChain = None
    currentLen = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}/chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > currentLen and blockchain.checkChainValidity(chain):
            currentLen = length
            longestChain = chain

    if longestChain:
        blockchain = longestChain
        return True

    return False


@app.route('/addBlock', methods=['POST'])
def verifyAndAddBlock():
    blockData = request.get_json()
    block = Block(blockData['idx'],
                  blockData['transactions'],
                  blockData['timestamp'],
                  blockData['previousHash'])
    proof = blockData['hash']
    added = blockchain.addBlock(block, proof)

    if not added:
        return 'The block was discarded by the node', 400
    return 'Block added...', 201


def announceNewBlock(block):
    for peer in peers:
        url = '{}addBlock'.format(peer)
        requests.post(url, data=json.dumps(block.__dict__, sort_keys=True))


@app.route('/mine', methods=['GET'])
def mineUnconfirmedTransactions():
    result = blockchain.mine()
    if not result:
        return 'No transactions to mine'
    else:
        chainLength = len(blockchain.chain)
        consensus()
        if chainLength == len(blockchain.chain):
            announceNewBlock(blockchain.lastBlock)
        return 'Block #{} is mined..'.format(blockchain.lastBlock.idx)


