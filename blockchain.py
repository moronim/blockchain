"""
This is what a block should look like

block = {
    'index': 1,
    'timestamp': 1506057125.900785,
    'transactions': [
        {
            'sender': "8527147fe1f5426f9dd545de4b27ee00",
            'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
            'amount': 5,
        }
    ],
    'proof': 324984774000,
    'previous_hash': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
}
"""

import hashlib
import json
from textwrap import dedent
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
	"""docstring fos Blockchain"""
	def __init__(self):
		self.chain = []
		self.current_transactions = []

		# Creates the Genesis block

		self.new_block(previous_hash=1, proof=100)


	def new_block(self, proof, previous_hash=None):
		"""
		Create a new block in the blockchain

		:param proof: <int> The proof given by the Proof of Work algorithm
		:param previous_hash: (Optional) <str> Hash of a previous block
		:return <dict> New Block
		"""

		block = {
			'index': len(self.chain) + 1,
			'timestamp': time(),
			'transactions': self.current_transactions,
			'proof': proof,
			'previous_hash': previous_hash or self.hash(self.chain[-1])
		}

		# reset the current list of transactions
		self.current_transactions = []

		self.chain.append(block)
		return block


	def new_transaction(self, sender, recipient, amount):
		"""
		Creates a new transaction and add it to the block

		:param sender: <str> Address of sender
		:param recipient <str> Address of recipients
		:param amount <int> Amount
		:return <int> The index of the Block that will hold this transaction
		"""

		self.current_transactions.append({
			'sender' : sender,
			'recipient' : recipient,
			'amount' : amount
			})

		return self.last_block['index'] + 1

	def proof_of_work(self, last_proof):
		"""
		
		Simple proof of work algorithm: 
		- Find a number p' that hash(pp') contains leading 4 zeros, where p is the previous p'
		- p is the previous proof, p' is the current proof

		:param last_proof: <int> Previous proof
		:return: <int>

		"""
		proof = 0
		while self.valid_proof(last_proof, proof) is False:
			proof += 1

		return proof

	@staticmethod
	def valid_proof(last_proof, proof):
		"""

		Validates the Proof: does hash(last_proof, proof) contsains 4 leading zeros?

		:param last_proof: <int> Previous proof 
		:param proof: <int> Current proof
		:return: <bool> True if correct, False if not
		
		"""

		guess = f'{last_proof}{proof}'.encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[:4] == '0000'

	@staticmethod
	def hash(block):
		"""
		Creates a SHA-256 hash of a block

		:param block: <dict> Block
		:return <str> 

		"""

		# We must make sure the dictionary is ordered or we'll have insconsistent hashes
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()


	@property
	def last_block(self):
		# Returns the last block on the chain
		return self.chain[-1]

# Instantiate out Node

app = Flask(__name__)

# Generate a globally unique address for this node 
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
	# We run the proof of work algorithm to get the next proof...
	last_block = blockchain.last_block
	last_proof = last_block['proof']
	proof = blockchain.proof_of_work(last_proof)

	# We must receive a reward for finding the proof
	# The sender is "0" to signify this node has mined a new coin
	blockchain.new_transaction(
		sender = "0",
		recipient = node_identifier,
		amount = 1,
	)

	# Forge a new block by adding it to the chain
	previous_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof, previous_hash)

	response = {
		'message': "New Block Forged",
		'index': block['index'],
		'transactions': block['transactions'],
		'proof': block['proof'],
		'previous_hash': block['previous_hash'],

	}
	return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json(force=True)
    print(values)
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    print (required)
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201
    
@app.route('/chain', methods=['GET'])
def full_chain():
	response = {
		'chain': blockchain.chain,
		'length': len(blockchain.chain)
	}
	return jsonify(response), 200

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)

	

		