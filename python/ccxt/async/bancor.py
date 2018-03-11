# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async.base.exchange import Exchange
import base64
import hashlib
import math
import json
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import AuthenticationError
from ccxt.base.errors import InsufficientFunds
from ccxt.base.errors import InvalidOrder
from ccxt.base.errors import OrderNotFound
from ccxt.base.errors import InvalidNonce


class bancor (Exchange):
    #order_agg_limit=[1,2,5,8,10]
    order_agg_limit = [1, 2]

    def describe(self):
        return self.deep_extend(super(bancor, self).describe(), {
            'id': 'bancor',
            'name': 'bancor',
            'countries': 'HK',  # Hong Kong
            'version': '0.1',
            'rateLimit': 1000,
            'userAgent': self.userAgents['chrome'],
            'has': {
                'CORS': False,
                'cancelOrders': False,
                'createMarketOrder': False,
                'fetchDepositAddress': False,
                'fetchTickers': False,
                'fetchOHLCV': False,  # see the method implementation below
                'fetchOrder': False,
                'fetchOrders': False,
                'fetchClosedOrders': False,
                'fetchOpenOrders': False,
                'fetchMyTrades': False,
                'fetchCurrencies': False,
                'withdraw': False,
            },
            'timeframes': {
                '1m': 1,
                '5m': 5,
                '15m': 15,
                '30m': 30,
                '1h': 60,
                '8h': 480,
                '1d': 'D',
                '1w': 'W',
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/33795655-b3c46e48-dcf6-11e7-8abe-dc4588ba7901.jpg',
                'api': {
                    'public': 'https://api.bancor.network',
                },
                'www': 'https://bancor.network',
            },
            'api': {
                'public': {
                    'get': [
                        'currencies/rate',
                        'currencies/{currencyId}/value',
                        'currencies/tokens',
                        'currencies',
                    ],
                },
            },
        })

    async def fetch_markets(self, params={}):
        #https://api.bancor.network/0.1/currencies/?type=ethereum&stage=traded&skip=0&limit=100&excludeSubTypes=bounty,relay
        parameter = {'type': 'ethereum',
                     'stage': 'traded',
                     'skip': '0',
                     'limit': '100',
                     'excludeSubTypes': 'bounty,relay',
                     }
        response = await self.publicGetCurrencies(self.extend(parameter, params))
        markets = response['data']['currencies']['page']
        result = []
        for i in range(0,len(markets)):
            market = markets[i]
            id = market['_id']
            symbol = market['code']
            type = market['type']
            code = market['code']
            contractAddress = market['details']['contractAddress']
            status = market['status']
            numDecimalDigits = market['numDecimalDigits']
            name = market['name']
            stage = market['stage']
            result.append({
                'id': id,
                'symbol': symbol,
                'code': code,
                'numDecimalDigits': numDecimalDigits,
                'name': name,
                'type':type,
                'contractAddress': contractAddress,
                'status': status,
                'stage': stage,
            })
        return result

    async def getRate(self,symbol,amount,params={}):
        return await self.convertByAmount(symbol.split('/')[1],symbol.split('/')[0],amount)

    async def convertByAmount(self,fromCurrency,toCurrency,fromAmount,params={}):
        await self.load_markets()
        parameter = {
            "currencyId": self.markets[fromCurrency]['id'],
            "toCurrencyId": self.markets[toCurrency]['id'],
            "fromAmount": fromAmount*10**int(self.markets[fromCurrency]['numDecimalDigits'])
        }
        response = await self.publicGetCurrenciesCurrencyIdValue(self.extend(parameter, params))
        toAmount = int(response['data']) / 10**int(self.markets[toCurrency]['numDecimalDigits'])
        toAmount = round(toAmount,8)
        return toAmount

    async def fetch_agg_order_book(self,symbol,limit=None,params={}):
        timestamp = self.milliseconds()
        symbol_reserved = symbol.split('/')[1]+'/'+symbol.split('/')[0]
        asks = []
        bids = []
        for i in self.order_agg_limit:
            amt_t = await self.getRate(symbol,i)
            asks.append([i/amt_t,amt_t])
            bids.append([await self.getRate(symbol_reserved,amt_t)/amt_t,amt_t])
        return {
            'bids': bids,
            'asks': asks,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
        }

    async def fetch_order_book(self, symbol, limit=None, params={}):
        return await self.fetch_agg_order_book(symbol,limit)

    def parse_order(self, order, market=None):
        symbol = None
        # if market:
        #     symbol = market['symbol']
        # else:
        #     symbol = order['coinType'] + '/' + order['coinTypePair']
        # timestamp = self.safe_value(order, 'createdAt')
        # price = self.safe_float(order, 'price')
        # if price is None:
        #     price = self.safe_float(order, 'dealPrice')
        # if price is None:
        #     price = self.safe_float(order, 'dealPriceAverage')
        # if price is None:
        #     price = self.safe_float(order, 'orderPrice')
        # remaining = self.safe_float(order, 'pendingAmount')
        # status = self.safe_value(order, 'status')
        # filled = self.safe_float(order, 'dealAmount')
        # if status is None:
        #     if remaining is not None:
        #         if remaining > 0:
        #             status = 'open'
        #         else:
        #             status = 'closed'
        # if filled is None:
        #     if status is not None:
        #         if status == 'closed':
        #             filled = self.safe_float(order, 'amount')
        # amount = self.safe_float(order, 'amount')
        # cost = self.safe_float(order, 'dealValue')
        # if cost is None:
        #     cost = self.safe_float(order, 'dealValueTotal')
        # if filled is not None:
        #     if price is not None:
        #         if cost is None:
        #             cost = price * filled
        #     if amount is None:
        #         if remaining is not None:
        #             amount = self.sum(filled, remaining)
        #     elif remaining is None:
        #         remaining = amount - filled
        # if (status == 'open') and(cost is None):
        #     cost = price * amount
        # side = self.safe_value(order, 'direction')
        # if side is None:
        #     side = order['type']
        # if side is not None:
        #     side = side.lower()
        # feeCurrency = None
        # if market:
        #     feeCurrency = market['quote'] if (side == 'sell') else market['base']
        # else:
        #     feeCurrencyField = 'coinTypePair' if (side == 'sell') else 'coinType'
        #     feeCurrency = self.safe_string(order, feeCurrencyField)
        #     if feeCurrency is not None:
        #         if feeCurrency in self.currencies_by_id:
        #             feeCurrency = self.currencies_by_id[feeCurrency]['code']
        # feeCost = self.safe_float(order, 'fee')
        # fee = {
        #     'cost': self.safe_float(order, 'feeTotal', feeCost),
        #     'rate': self.safe_float(order, 'feeRate'),
        #     'currency': feeCurrency,
        # }
        # # todo: parse order trades and fill fees from 'datas'
        # # do not confuse trades with orders
        # orderId = self.safe_string(order, 'orderOid')
        # if orderId is None:
        #     orderId = self.safe_string(order, 'oid')
        # result = {
        #     'info': order,
        #     'id': orderId,
        #     'timestamp': timestamp,
        #     'datetime': self.iso8601(timestamp),
        #     'symbol': symbol,
        #     'type': 'limit',
        #     'side': side,
        #     'price': price,
        #     'amount': amount,
        #     'cost': cost,
        #     'filled': filled,
        #     'remaining': remaining,
        #     'status': status,
        #     'fee': fee,
        # }
        return result

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        endpoint = '/' + self.version + '/' + self.implode_params(path, params)
        url = self.urls['api'][api] + endpoint
        query = self.omit(params, self.extract_params(path))
        if api == 'private':
            self.check_required_credentials()
            # their nonce is always a calibrated synched milliseconds-timestamp
            nonce = self.milliseconds()
            queryString = ''
            nonce = str(nonce)
            if query:
                queryString = self.rawencode(self.keysort(query))
                url += '?' + queryString
                if method != 'GET':
                    body = queryString
            auth = endpoint + '/' + nonce + '/' + queryString
            payload = base64.b64encode(self.encode(auth))
            # payload should be "encoded" as returned from stringToBase64
            signature = self.hmac(payload, self.encode(self.secret), hashlib.sha256)
            headers = {
                'KC-API-KEY': self.apiKey,
                'KC-API-NONCE': nonce,
                'KC-API-SIGNATURE': signature,
            }
        else:
            if query:
                url += '?' + self.urlencode(query)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}


    def throw_exception_on_error(self, response):
        #
        # API endpoints return the following formats
        #     {success: False, code: "ERROR", msg: "Min price:100.0"}
        #     {success: True,  code: "OK",    msg: "Operation succeeded."}
        #
        # Web OHLCV endpoint returns self:
        #     {s: "ok", o: [], h: [], l: [], c: [], v: []}
        #
        # This particular method handles API responses only
        #
        if not('success' in list(response.keys())):
            return
        if response['success'] is True:
            return  # not an error
        if not('code' in list(response.keys())) or not('msg' in list(response.keys())):
            raise ExchangeError(self.id + ': malformed response: ' + self.json(response))
        code = self.safe_string(response, 'code')
        message = self.safe_string(response, 'msg')
        feedback = self.id + ' ' + self.json(response)
        if code == 'UNAUTH':
            if message == 'Invalid nonce':
                raise InvalidNonce(feedback)
            raise AuthenticationError(feedback)
        elif code == 'ERROR':
            if message.find('The precision of amount') >= 0:
                raise InvalidOrder(feedback)  # amount violates precision.amount
            if message.find('Min amount each order') >= 0:
                raise InvalidOrder(feedback)  # amount < limits.amount.min
            if message.find('Min price:') >= 0:
                raise InvalidOrder(feedback)  # price < limits.price.min
            if message.find('The precision of price') >= 0:
                raise InvalidOrder(feedback)  # price violates precision.price
        elif code == 'NO_BALANCE':
            if message.find('Insufficient balance') >= 0:
                raise InsufficientFunds(feedback)
        raise ExchangeError(self.id + ': unknown response: ' + self.json(response))

    def handle_errors(self, code, reason, url, method, headers, body, response=None):
        if response is not None:
            # JS callchain parses body beforehand
            self.throw_exception_on_error(response)
        elif body and(body[0] == '{'):
            # Python/PHP callchains don't have json available at self step
            self.throw_exception_on_error(json.loads(body))
