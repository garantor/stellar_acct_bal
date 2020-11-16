from flask_restful import Resource, Api, reqparse
from stellar_sdk import Server
from flask import Flask
import requests



app = Flask(__name__, template_folder='../sendit/templates')

api = Api(app)
server = Server(horizon_url="https://horizon.stellar.org")

# Asset with value below 0.05usd will be ignored

class Balance_endpoint(Resource):
    def post(self, *args):
        resquestparser = reqparse.RequestParser()
        resquestparser.add_argument('public_key', required=True,
                            type=str, help='Public key required')

        xdr_args = resquestparser.parse_args()
        address = xdr_args['public_key']
        transactions = server.accounts().account_id(address).call()
        newbal = transactions['balances']
        asset = newbal
        total_bal = {}
        for i in range(len(asset)):
            if float(asset[i]['balance']) != 0.00:
                try:
                    from_code = asset[i]['asset_code']
                    from_bal = asset[i]['balance']
                    total_bal[from_code] = from_bal
                except KeyError:
                    from_code = 'XLM'
                    from_bal = asset[i]['balance']
                    total_bal[from_code] = from_bal

        url = f"https://horizon.stellar.org/paths/strict-receive?source_account={address}&destination_asset_type=credit_alphanum4&destination_asset_issuer=GDUKMGUGDZQK6YHYA5Z6AY2G4XDSZPSZ3SW5UN3ARVMO6QSRDWP5YLEX&destination_asset_code=USD&destination_amount=0.05"
        a = requests.get(url)
        b = a.json()


        unit_price = {}
        for i in range(len(b['_embedded']['records'])):
            try:
                code = b['_embedded']['records'][i]['source_asset_code']
                amount = b['_embedded']['records'][i]['source_amount']
                unit_price[code]= amount
            except Exception as e:
                code = 'XLM'
                amount = b['_embedded']['records'][i]['source_amount']
                unit_price[code]= amount

        final = []
        
        for key, value in unit_price.items():
            if key in total_bal:
                main_usd = float(total_bal[key]) / float(value)
                indi_bal = main_usd * 0.05
                final.append(indi_bal)
        return sum(final)


api.add_resource(Balance_endpoint, '/api/v1/balance')


if __name__ == "__main__":
    app.run(debug=True)