import os
import sys

from flask import Flask
from flask import request
from flask import jsonify

from spool import Wallet

from register_work import generate_notarise_tx, push_tx


app = Flask(__name__)






# 
# Error handler
# 
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response




def notarise(data):
	tx_hex = ''
	
	if(len(data) < 16):
		raise InvalidUsage('Data needs to be 16+ bytes', status_code=400)

	try:
		int(data, 16)
	except ValueError as ex:
		raise InvalidUsage('Data needs to be in hexadecimal form', status_code=400)

	data_prefixed = DATA_PREFIX + str(data)

	if(len(data_prefixed) > 80):
		raise InvalidUsage('Data needs to be 80 bytes or less', status_code=400)

	try:
		tx_hex = generate_notarise_tx(fed_wallet.root_address[1], FEDERATION_WALLET_SECRET, data_prefixed)
	except Exception as e:
		raise e

	return push_tx(tx_hex)



# 
# Actual API
# 

@app.route('/')
def index():
	return "Fund wallet address %s\n Federation wallet address %s" % (fund_wallet.root_address[1], fed_wallet.root_address[1])


@app.route("/notarise", methods = ['POST'])
def api_notarise():
	# try:
	data = request.form['data']
	auth_token = request.form['token']

	print("POST with "+data)

	if(auth_token != AUTH_TOKEN):
		raise InvalidUsage('Not authorized for token', status_code=403)

	return notarise(data)





if __name__ == "__main__":
	ip = sys.argv[1]


	# Temporary measure to stop outsiders from using service.
	AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
	# Prefix for data inserted in OP_RETURN
	DATA_PREFIX = 'VDICT '

	FUND_WALLET_SECRET = os.environ.get('FUND_WALLET_SECRET').encode('utf-8')
	FEDERATION_WALLET_SECRET = os.environ.get('FED_WALLET_SECRET').encode('utf-8')

	if not AUTH_TOKEN or not FUND_WALLET_SECRET or not FEDERATION_WALLET_SECRET:
		raise Exception("Bad config")


	fund_wallet = Wallet(FUND_WALLET_SECRET)
	fed_wallet = Wallet(FEDERATION_WALLET_SECRET)

	print("Fund wallet: %s" % fund_wallet.root_address[1])
	print("Federation wallet: %s" % fed_wallet.root_address[1])



	app.run(host=ip, threaded=True)


