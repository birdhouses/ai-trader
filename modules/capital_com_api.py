import requests
import hashlib
import hmac
import base64
import time

class CapitalComAPI:
    def __init__(self, api_key, identifier, password, base_url='https://api-capital.backend-capital.com/', demo=False):
        self.api_key = api_key
        self.identifier = identifier
        self.password = password
        self.session_token = None
        self.security_token = None
        self.base_url = base_url if not demo else 'https://demo-api-capital.backend-capital.com/'
        self.headers = {
            'X-CAP-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        self.start_session()

    def start_session(self):
        """Start a new session and obtain session tokens"""
        url = self.base_url + 'api/v1/session'
        payload = {
            "identifier": self.identifier,
            "password": self.password,
            "encryptedPassword": False
        }
        response = requests.post(url, headers=self.headers, json=payload)
        print(response)
        if response.status_code == 200:
            self.session_token = response.headers['CST']
            self.security_token = response.headers['X-SECURITY-TOKEN']
            self.headers.update({
                'CST': self.session_token,
                'X-SECURITY-TOKEN': self.security_token
            })
        else:
            raise Exception(f"Failed to start session: {response.text}")

    def ping(self):
        """Ping the service to keep the session alive"""
        url = self.base_url + 'api/v1/ping'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def end_session(self):
        """End the current session"""
        url = self.base_url + 'api/v1/session'
        response = requests.delete(url, headers=self.headers)
        return response.json()

    def get_accounts(self):
        """Retrieve all accounts associated with the current session"""
        url = self.base_url + 'api/v1/accounts'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_account_preferences(self):
        """Retrieve account preferences like leverage settings and trading mode"""
        url = self.base_url + 'api/v1/accounts/preferences'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def update_account_preferences(self, leverages=None, hedging_mode=None):
        """Update account preferences such as leverage settings and trading mode"""
        url = self.base_url + 'api/v1/accounts/preferences'
        payload = {}
        if leverages:
            payload['leverages'] = leverages
        if hedging_mode is not None:
            payload['hedgingMode'] = hedging_mode
        response = requests.put(url, headers=self.headers, json=payload)
        return response.json()

    def get_market_categories(self):
        """Retrieve all top-level market categories"""
        url = self.base_url + 'api/v1/marketnavigation'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_category_markets(self, node_id, limit=500):
        """Retrieve all sub-markets for a given market category"""
        url = f"{self.base_url}api/v1/marketnavigation/{node_id}?limit={limit}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def search_markets(self, search_term=None, epics=None):
        """Search for markets by term or by EPIC"""
        url = self.base_url + 'api/v1/markets'
        params = {}
        if search_term:
            params['searchTerm'] = search_term
        if epics:
            params['epics'] = ','.join(epics)
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_market_details(self, epic):
        """Retrieve detailed information for a specific market"""
        url = f"{self.base_url}api/v1/markets/{epic}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_historical_prices(self, epic, resolution='MINUTE', max=10, from_date=None, to_date=None):
        """Retrieve historical prices for a specific market"""
        url = f"{self.base_url}api/v1/prices/{epic}"
        params = {
            'resolution': resolution,
            'max': max
        }
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_client_sentiment(self, market_ids):
        """Retrieve client sentiment for specific markets"""
        url = f"{self.base_url}api/v1/clientsentiment"
        params = {
            'marketIds': ','.join(market_ids)
        }
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def create_position(self, epic, direction, size, guaranteed_stop=False, stop_level=None, profit_level=None):
        """Create a new trading position"""
        url = self.base_url + 'api/v1/positions'
        payload = {
            "epic": epic,
            "direction": direction,
            "size": size,
            "guaranteedStop": guaranteed_stop
        }
        if stop_level:
            payload['stopLevel'] = stop_level
        if profit_level:
            payload['profitLevel'] = profit_level
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def close_position(self, deal_id):
        """Close an open trading position"""
        url = f"{self.base_url}api/v1/positions/{deal_id}"
        response = requests.delete(url, headers=self.headers)
        return response.json()

    def create_working_order(self, epic, direction, size, level, order_type='LIMIT', guaranteed_stop=False, stop_level=None, profit_level=None, good_till_date=None):
        """Create a new working order"""
        url = self.base_url + 'api/v1/workingorders'
        payload = {
            "epic": epic,
            "direction": direction,
            "size": size,
            "level": level,
            "type": order_type,
            "guaranteedStop": guaranteed_stop
        }
        if stop_level:
            payload['stopLevel'] = stop_level
        if profit_level:
            payload['profitLevel'] = profit_level
        if good_till_date:
            payload['goodTillDate'] = good_till_date
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def update_working_order(self, deal_id, level=None, good_till_date=None, guaranteed_stop=None, stop_level=None, profit_level=None):
        """Update an existing working order"""
        url = f"{self.base_url}api/v1/workingorders/{deal_id}"
        payload = {}
        if level:
            payload['level'] = level
        if good_till_date:
            payload['goodTillDate'] = good_till_date
        if guaranteed_stop is not None:
            payload['guaranteedStop'] = guaranteed_stop
        if stop_level:
            payload['stopLevel'] = stop_level
        if profit_level:
            payload['profitLevel'] = profit_level
        response = requests.put(url, headers=self.headers, json=payload)
        return response.json()

    def delete_working_order(self, deal_id):
        """Delete an existing working order"""
        url = f"{self.base_url}api/v1/workingorders/{deal_id}"
        response = requests.delete(url, headers=self.headers)
        return response.json()

    def get_open_positions(self):
        """Retrieve all open positions for the active account"""
        url = self.base_url + 'api/v1/positions'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_open_orders(self):
        """Retrieve all open working orders for the active account"""
        url = self.base_url + 'api/v1/workingorders'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_position(self, deal_id):
        """Retrieve details of a specific open position"""
        url = f"{self.base_url}api/v1/positions/{deal_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_order(self, deal_id):
        """Retrieve details of a specific open working order"""
        url = f"{self.base_url}api/v1/workingorders/{deal_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

    def get_account_activity(self, from_date=None, to_date=None, last_period=600, detailed=False, deal_id=None, filter=None):
        """Retrieve account activity history"""
        url = f"{self.base_url}api/v1/history/activity"
        params = {
            'lastPeriod': last_period,
            'detailed': detailed
        }
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        if deal_id:
            params['dealId'] = deal_id
        if filter:
            params['filter'] = filter
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def get_transaction_history(self, from_date=None, to_date=None, last_period=600, transaction_type=None):
        """Retrieve transaction history"""
        url = f"{self.base_url}api/v1/history/transactions"
        params = {
            'lastPeriod': last_period
        }
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        if transaction_type:
            params['type'] = transaction_type
        response = requests.get(url, headers=self.headers, params=params)
        return response.json()

    def adjust_demo_balance(self, amount):
        """Adjust the balance of the current Demo account"""
        url = f"{self.base_url}api/v1/accounts/topUp"
        payload = {
            'amount': amount
        }
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def get_watchlists(self):
        """Retrieve all watchlists belonging to the current user"""
        url = self.base_url + 'api/v1/watchlists'
        response = requests.get(url, headers=self.headers)
        return response.json()

    def create_watchlist(self, name, epics=None):
        """Create a new watchlist"""
        url = self.base_url + 'api/v1/watchlists'
        payload = {
            "name": name
        }
        if epics:
            payload['epics'] = epics
        response = requests.post(url, headers=self.headers, json=payload)
        return response.json()

    def delete_watchlist(self, watchlist_id):
        """Delete an existing watchlist"""
        url = f"{self.base_url}api/v1/watchlists/{watchlist_id}"
        response = requests.delete(url, headers=self.headers)
        return response.json()

    def add_market_to_watchlist(self, watchlist_id, epic):
        """Add a market to a watchlist"""
        url = f"{self.base_url}api/v1/watchlists/{watchlist_id}"
        payload = {
            "epic": epic
        }
        response = requests.put(url, headers=self.headers, json=payload)
        return response.json()

    def remove_market_from_watchlist(self, watchlist_id, epic):
        """Remove a market from a watchlist"""
        url = f"{self.base_url}api/v1/watchlists/{watchlist_id}/{epic}"
        response = requests.delete(url, headers=self.headers)
        return response.json()
