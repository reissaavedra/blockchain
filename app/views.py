import datetime
import json

import requests
from flask import render_template, redirect, request

from app import app

# The node with which our application interacts, there can be multiple such nodes as well.
CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8000"

posts = []


def fetchPosts():
    getChainAddress = '{}/chain'.format(CONNECTED_NODE_ADDRESS)
    response = requests.get(getChainAddress)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)
        for block in chain['chain']:
            for tx in block['transactions']:
                tx['idx'] = block['idx']
                tx['hash'] = block['previousHash']
                content.append(tx)

        global posts
        posts.sorted(content,
                     key=lambda k: k['timestamp'],
                     reverse=True)


@app.route('/submit', methods=['POST'])
def submitTxtArea():
    postContent = request.form['content']
    author = request.form['author']

    postObject = {
        'author': author,
        'content': postContent
    }

    newTxAddress = '{}/newTransaction'.format(CONNECTED_NODE_ADDRESS)
    requests.post(newTxAddress, json=postObject,
                  headers={
                      'Content-Type': 'application/json'
                  })

    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
