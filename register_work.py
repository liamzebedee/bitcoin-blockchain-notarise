from __future__ import unicode_literals
"""
A simplified client to notarising documents on the Bitcoin blockchain.

Uses the Ascribe.io SPOOL library to 
 - manage generating addresses, 
 - selecting tx inputs/outputs and 
 - building txs

"""
from spool import Spool
from spool import Wallet

from bitcoin import bin_hash160, bin_to_b58check

import hashlib
from builtins import object, str, super
import sys
import os

_magicbyte = 111
spool = Spool()
min_confirmations = 0


# Federation wallet is responsible for maintaining a list of addresses that contain just enough Bitcoin for sending custom OP_RETURN transactions.

def fund_federation_wallet(fed_wallet, fund_wallet, fund_wallet_secret):
	from_address = fund_wallet.root_address[1]
	to_address = fed_wallet.root_address[1]
	nfees = int(os.environ.get('NFEES'))
	ntokens = int(os.environ.get('NTOKENS'))

	unsigned_tx = spool._t.simple_transaction(from_address,
											 [(to_address, spool.FEE)] * nfees + [(to_address, spool.TOKEN)] * ntokens,
											 min_confirmations=min_confirmations)
	signed_tx = spool._t.sign_transaction(unsigned_tx, fund_wallet_secret)
	return signed_tx

# Generate tx to notarise data on blockchain
def generate_notarise_tx(fed_address, fed_pass, data_to_notarise):
	unsigned_tx = spool.simple_spool_transaction(fed_address,
                                                [fed_address],
                                                op_return=str(data_to_notarise),
                                                min_confirmations=min_confirmations)

	signed_tx = spool._t.sign_transaction(unsigned_tx, fed_pass)

	return signed_tx

# def generate_unqiue_addr_for_path(wallet, path):
# 	gendPath, addr = wallet.address_from_path(path)
# 	print("Generated address %s from %s" % addr, gendPath)

def gen_address_for_data(data):
	print("Hashing data: "+str(data))

	# https://gist.github.com/patricklodder/b27fb3e91c0566272976#file-gistfile1-py-L390
	# RIPEMD160(SHA256(data))
	fingerprint = bin_hash160(data.encode())
	print("Data fingerprint: "+str(fingerprint.encode('hex')))

	address = str(bin_to_b58check(fingerprint), magicbyte=_magicbyte)
	print("Final address: "+str(address))

	return address



def pushTx(tx):
	tx_id = spool._t.push(tx)
	print("Pushed tx %s" % tx_id)




if __name__ == "__main__":
	cmd = sys.argv[1]

	FUND_WALLET_SECRET = os.environ.get('FUND_WALLET_SECRET')
	FEDERATION_WALLET_SECRET = os.environ.get('FED_WALLET_SECRET')

	fund_wallet = Wallet(FUND_WALLET_SECRET)
	fed_wallet = Wallet(FEDERATION_WALLET_SECRET)

	if cmd == 'fund':
		print("Funding federation wallet %s..." % fed_wallet.root_address[1])
		tx = fund_federation_wallet(fed_wallet, fund_wallet, FUND_WALLET_SECRET)
		txid = pushTx(tx)
		print("https://www.blocktrail.com/BTC/tx/%s" % txid)

	elif cmd == 'notarise':

		data = sys.argv[2]
		if(len(data) < 16):
			print("Data needs to be 16+ bytes")
			raise Exception

		data_prefixed = "TEST"+str(data)
		if(len(data_prefixed) > 80):
			print("Data needs to be 80 bytes or less")
			raise Exception

		print('Notarising data...')

		tx_hex = generate_notarise_tx(fed_wallet.root_address[1], fed_wallet_secret, data_prefixed)
		pushTx(tx_hex)

	else:
		print("Syntax: registerWorkSimple.py (fund | notarise) <data>")
	
	exit(0)













