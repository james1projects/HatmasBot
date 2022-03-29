"""Mix it up developer api."""

import json
import requests


def pretty_print(json_string):
    """Print a json string as a readable format.

    Parameters
    ----------
    json_string : String
        String in json format.

    Returns
    -------
    None.
    """
    json_formatted_str = json.dumps(json_string, indent=2)
    print(json_formatted_str)


class MixClient():
    """Access the mix it up developer api.

    Documentation: https://saviorxtanren.github.io/mixer-mixitup/#section/Introduction
    """

    def __init__(self):
        self.mix_base_url = "http://localhost:8911/api/"

    def pretty_print(self, json_string):
        """Print a json string as a readable format.

        Parameters
        ----------
        json_string : String
            String in json format.

        Returns
        -------
        None.
        """
        json_formatted_str = json.dumps(json_string, indent=2)
        print(json_formatted_str)

    def get_request(self, endpoint):
        """Make a get request to the mix it up api.

        Parameters
        ----------
        url : String
            Full url for the request.

        Returns
        -------
        final_result : dictionary
            status: the request status
            result: the result from request (might not be included)
        """
        url = self.mix_base_url + endpoint
        final_result = {}
        req_result = requests.get(url)
        final_result['status'] = req_result.status_code
        if final_result['status'] != 200:
            # Something went wrong with request
            print(url, 'status code is', final_result['status'])

        try:
            final_result['result'] = req_result.json()
        except Exception as e:
            print("Could not use req_result.json()\n", e)

        return final_result

    def put_request(self, endpoint, put_info):
        """Make a put request to the mix it up api.

        Parameters
        ----------
        url : String
            Full url for the request.
        put_info : Dictionary/List in json format.
            Dictionary/List in json format with info for the request.

        Returns
        -------
        final_result : dictionary
            status: the request status
            result: the result from request (might not be included)
        """
        final_result = {}
        url = self.mix_base_url + endpoint
        req_result = requests.put(url, json=put_info)
        final_result['status'] = req_result.status_code
        if final_result['status'] != 200:
            # Something went wrong with request
            print(url, 'status code is', final_result['status'])

        try:
            final_result['result'] = req_result.json()
        except Exception as e:
            print("Could not use req_result.json()\n", e)

        return final_result

    def post_request(self, endpoint, post_info):
        """Make a put request to the mix it up api.

        Parameters
        ----------
        url : String
            Full url for the request.
        post_info : Dictionary/List in json format.
            Dictionary/List in json format with info for the request.

        Returns
        -------
        final_result : dictionary
            status: the request status
            result: the result from request (might not be included)
        """
        final_result = {}
        url = self.mix_base_url + endpoint
        print(url)
        print(type(post_info))
        pretty_print(post_info)
        req_result = requests.post(url, json=post_info)
        final_result['status'] = req_result.status_code
        if final_result['status'] != 200:
            # Something went wrong with request
            print(url, 'status code is', final_result['status'])

        try:
            final_result['result'] = req_result.json()
        except Exception as e:
            print("Could not use req_result.json()\n", e)

        return final_result

    def get_user(self, username_or_id):
        """Get user data by username/ID.

        Parameters
        ----------
        username_or_id : String
            Username or id

        Returns
        -------
        final_result : Dictionary
            Dictionary of user.
            ID: mix it up user id
            TwitchID: Twitch ID
            Username: username
            ViewingMinutes: minutes in stream
            CurrencyAmounts: <List> of currencies
            InventoryAmounts: <List> of inventory
        """
        return self.get_request("/users/" + username_or_id).get('result', None)

    def set_user_currency(self, mix_user_id, currency_dictionary, currency_amount):
        """Set the user currency to a specific amount.

        Parameters
        ----------
        mix_user_id : String
            mix it up user id.
        currency_dictionary : dictionary
            A currency dictionary with info about the currency to be changed.
            Can get this with get_currency(currency_name)
        currency_amount : int
            The amount to set the currency to.

        Returns
        -------
        final_result : json/dictionary
            The new user info from mix it up.
            ID: mix it up id.
            TwitchID: Twitch ID
            Username: username
            ViewingMinutes: Minutes in stream
            CurrencyAmounts: <List> of currencies
            InventoryAmounts: <List> of inventory

        """
        post_info = {}
        post_info["ID"] = mix_user_id
        currency_dictionary["Amount"] = currency_amount
        post_info["CurrencyAmounts"] = [currency_dictionary]

        return self.put_request("users/" + mix_user_id, post_info).get('result', None)

    def get_all_currencies(self):
        """Get all currencies.

        Returns
        -------
        List
            List of currencies

        """
        return self.get_request("/currency")

    def get_currency(self, currency_name):
        """Get a currency dictionary by name.

        Parameters
        ----------
        currency_name : String
            The currency name.

        Returns
        -------
        currency_dictionary : Dictionary (Or None if not found.)
            Dictionary for currency.
            ID: The currency id.
            Name: The currency name.
        """
        currency_dictionary = None
        currency_name = currency_name.lower()
        currencies = self.get_all_currencies()
        if currencies is not None:
            # Currency request was successful and we have a list of currencies.
            for currency in currencies:
                if currency['Name'].lower() == currency_name:
                    # Found the currency we are looking for
                    currency_dictionary = currency
                    break
        return currency_dictionary

    def get_multiple_users(self, array_users):
        """Get multiple user info from mix it up api.

        Parameters
        ----------
        array_users : List of Strings
            Array of users to get user info for. Should be mix it up user id,
            or twitch usernames.

        Returns
        -------
        List of dictionaries
            List of dictionaries containing user info.

        """
        return self.post_request("users", array_users)

    def add_currency(self, username_or_id, currency_id, amount):
        """Add an amount to the currency for a user.

        Has a status of 403 if the user does not have enough of the chosen currency.

        Parameters
        ----------
        username_or_id : String
            Their username or mix it up id.
        currency_id : String
            The currency id.
        amount : int
            Amount to add to the current currency (can be negative).

        Returns
        -------
        Dictionary
            Dictionary of new user info.

        """
        amount = {"Amount": amount}
        return self.put_request("users/" + username_or_id + "/currency/" +
                                currency_id + "/adjust", amount).get('result', None)

    def add_inventory(self, username_or_id, inventory_id, item_name, amount):
        """Add inventory for the user.

        Parameters
        ----------
        username_or_id : String
            Their username or mix it up id.
        inventory_id : String
            The inventory id.
        item_name : String
            The item name in the inventory.
        amount : int
            Amount to add of the item for the inventory (can be negative).

        Returns
        -------
        Dictionary
            Dictionary of new user info.

        """
        inventory = {"Name": item_name,
                     "Amount": amount}
        return self.put_request("users/" + username_or_id + "/inventory/" +
                                inventory_id + "/adjust", inventory).get('result', None)

    def get_top_time(self, number=10):
        """Get the top users based on most time watched.

        Parameters
        ----------
        number : int
            Number of users to get from the top.
            Default is 10.

        Returns
        -------
        List of dictionaries
            List of dictionaries containing user info.
        """
        return self.get_request("users/top?count=" + str(number)).get('result', None)

    def get_top_currency(self, currency_id, number=10):
        """Get the top users based on those who have the most currency.

        Parameters
        ----------
        currency_id : String
            The currency id.
        number : int
            Number of users to get from the top.
            Default is 10.

        Returns
        -------
        List of dictionaries
            List of dictionaries containing user info.
        """
        return self.get_request("currency/" + currency_id + "/top?count=" + str(number)).get('result', None)

    def get_active_users(self):
        """Get a list of user info for all active users.

        Note: This might only work when live? Not currently tested.

        Returns
        -------
        List
            List of dictionaries of user info for active users..

        """
        return self.get_request("chat/users").get('result', None)

    def give_user_list_currency(self, currency_id, user_list):
        """Give all users in a list a specific amount of currency.

        Parameters
        ----------
        currency_id : String
            The currency id.
        user_list : List
            List of usernames with amount to give.
            Amount: int
            UsernameOrId: username or id
        Returns
        List
            List of dictionaries of user info for new user info.
        """
        return self.get_request("currency/" + currency_id + "/give").get('result', None)

    def send_message(self, message, send_as_streamer = False):
        """Send a message in the chat.

        Parameters
        ----------
        message : String
            The message to send.
        send_as_streamer : Boolean, optional
            Whether to send as the streamer or not. The default is False.

        Returns
        -------
        None.

        """
        post_info = {"Message": message}
        print(post_info)

        self.post_request("chat/sendchatmessage", post_info).get('result', None)

if __name__ == "__main__":
    print('Running mix_it_up.py as main method..')
    mix_client = MixClient()
    mix_client.send_message("Hello")
    # pretty_print(mix_client.add_currency("fb2e3bcf-5ad4-4898-8507-e8e5dd903a39", "12e3a8ff-06db-482d-9842-d018e475cbbc", 10))