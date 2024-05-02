import hashlib
import json
from time import time
from urllib.parse import urlparse

import requests



class Blockchain(object):
    def __init__(self):
        self.chain=[]
        self.current_transaction=[]
        self.nodes = set()

        self.new_block(previous_hash='1', proof = 100)

    def new_block(self,proof, previous_hash=None):
        """

        :param proof:<int> Proof by the proof of work algo
        :previous_hash:(Optional) <str> Hash of the previous block
        :return:<dict> New block
        """
        block={
            'index': len(self.chain)+1,
            'timestamp': time(),
            'transactions' : self.current_transaction,
            'proof':proof,
            'previous_hash':previous_hash or self.hash(self.chain[-1]),
        }

        self.current_transaction=[]

        self.chain.append(block)
        return block
    
    def new_transaction(self, sender, recepient, amount):
        """
        Creates a new transaction into the next mined block
        :param sender: <str> sender addeess
        :param recepint:<str> recepient address
        :param amount: <int> amount
        :return:<int> index of the block
        """
        self.current_transaction.append({
            'sender': sender,
            'recepient': recepient,
            'amount': amount,
        })

        return self.last_block['index']+1
    
    @property
    def last_block(self):
        return self.chain[-1]
    
    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block:<dict> Block
        :return:<str>
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()



    def proof_of_work(self, last_proof):
        """
        Simple proof of work Algorithm:
        - Find a number p' such that hash(pp') contains leading 4 zeroes,
        - p is the previous proof of work and p' is the new proof
        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.validProof(last_proof, proof) is False:
            proof += 1

        return proof
    @staticmethod
    def validProof(last_proof,proof):
        """
        Validates the proof: Does hash(last_proof, proof) constains 4 leading zeroes, where p is previous p'
        :param last_proof:<int> Previous proof
        :param proof: <int> Current proof
        :return: <bool> True if correct, else False 
        """

        guess = f'{last_proof},{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4]=="0000"
    
    def register_nodes(self,address):
        """
        add new node to the list of nodes
        : param address = <str> Address of node
        :return : none
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: <list> A blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.validProof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our Consensus Algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.
        :return: <bool> True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False
    


             
             
            

            

    
        

 
    
   
    
    
    
    
        
  