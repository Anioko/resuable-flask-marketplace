import requests


class Paystack(object):
    def __init__(self, token: str):
        self._token = token
        self.BASE_URL = 'https://api.paystack.co/transaction/initialize'

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, token: str):
        self._token = token

    def accept(self, amount: int, currency: str, email: str, description: str, metadata: dict,):
        """
        Accepts a payment.
        """
        headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json"
        }
        data = {
            "amount": amount,
            "currency": currency,
            "email": email,
            "description": description,
            "metadata": metadata
        }
        response = requests.post(self.BASE_URL, json=data, headers=headers)
        return response.json()


# token = 'sk_test_653403ae504d0e85e81e283569da9250fc763719'
# payment = Paystack(token)


# # initialize example payment with random data

# response = payment.accept(amount=1000, currency='ZAR', email='isaackeinstein@gmail.com',
#                           description='Payment for goods', metadata={'order_id': '1234'})

# print(response)
