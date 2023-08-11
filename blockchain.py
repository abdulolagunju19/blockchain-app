#!/usr/bin/python
# -*- coding: utf-8 -*-

from hashlib import sha256

# Function to update and return the hash value of concatenated arguments
def updatehash(*args):
    hashing_text = ''
    h = sha256()
    for arg in args:
        hashing_text += str(arg)

    h.update(hashing_text.encode('utf-8'))
    return h.hexdigest()

# Block class representing a block in the blockchain
class Block:

    def __init__(self, number=0, previous_hash="0"*64, data=None, nonce=0):
        self.data = data
        self.number = number
        self.previous_hash = previous_hash
        self.nonce = nonce

    # nonce is a number you set so that your hash will have a certain attribute(eg. 4 leading zeroes)
    # mining will look for a nonce that will create a hash that has a certain number of leading zeroes for your data
    
    # Calculate and return the hash value of the block
    def hash(self):
        return updatehash(
                        self.previous_hash,
                        self.number,
                        self.data,
                        self.nonce
                        )

    def __str__(self):
        return str(f"Block #: {self.number}\nHash: {self.hash()}\nPrevious: {self.previous_hash}\nData: {self.data}\nNonce: {self.nonce}\n")

class Blockchain:

    # Difficulty level for mining (number of leading zeros in hash)
    difficulty = 5

    def __init__(self):
        self.chain = []

    # Add a block to the chain
    def add(self, block):
        self.chain.append(block)

    # Remove a block from the chain
    def remove(self, block):
        self.chain.remove(block)

    # Mine a block by finding the appropriate nonce value
    def mine(self, block):

        # hashing the last block, throw error if its not there
        try:
            block.previous_hash = self.chain[-1].hash()
        except IndexError:
            pass
        while True:
            # Check if hash meets difficulty requirements
            if block.hash()[:self.difficulty] == '0' * self.difficulty:
                self.add(block)
                break
            else:
                block.nonce += 1

    def isValid(self):
        for i in range(1, len(self.chain)):
            _previous = self.chain[i].previous_hash
            _current = self.chain[i-1].hash()
            if(_previous != _current or _current[:self.difficulty] != "0"*self.difficulty):
                return False
        return True

# test whether the blockchain is valid after adding some test values
def main():
    blockchain = Blockchain()
    database = ['hello world', "What's up", 'hello', 'bye']

    num = 0
    for data in database:
        num += 1
        blockchain.mine(Block(data, num))

    for block in blockchain.chain:
        print(block)

    print(blockchain.isValid())

if __name__ == '__main__':
    main()
