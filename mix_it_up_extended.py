"""Use mix_it_up_api.py to create useful functions and commands with mix it up."""
import json
from mix_it_up_api import MixClient
import random


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


class MixClientExtended(MixClient):
    """Extend MixClient to create useful functions and commands from the api."""

    def gamble(self, twitch_username, gambled_amount):
        """Roll a number between 1-100. User is rewarded based on the roll.

        Include both the lower and upper bound.
        1-60: Loss
        61-97: Win (x2 reward)
        98-100: Win (x3 reward)

        NOTE: This command is currently hard coded for hats!!

        Parameters
        ----------
        twitch_username : String
            Twitch username.
        gambled_amount : String
            The amount the user has gambled.
            Can be 10 through anything, checks to see if they have enough.
            Can also use "all", "half", "quarter"

        Returns
        -------
        String
            Message to send after gamble command is done.
        """
        # TODO: This command is currently hard coded for hats! Fix that if ever released.
        gambled_amount = gambled_amount.lower()
        message = ""
        lowest_possible_roll = 1
        highest_possible_roll = 100
        minimum_wager = 100
        mix_user = self.get_user(twitch_username)
        if mix_user is not None:
            mix_user_id = mix_user['ID']
            currency_dictionary = mix_user['CurrencyAmounts'][0]
            currency_id = currency_dictionary['ID']
            currency_amount = currency_dictionary['Amount']
            currency_name = currency_dictionary['Name']

            if gambled_amount == "all":
                # Gamble all.
                gambled_number = currency_amount
            elif gambled_amount == "half":
                gambled_number = round(currency_amount / 2)
            elif gambled_amount == "quarter":
                gambled_number = round(currency_amount / 4)
            elif gambled_amount.isnumeric():
                gambled_number = int(gambled_amount)
            else:
                # Not a valid gamble parameter
                return message

            gambled_number = int(gambled_number)
            if gambled_number > currency_amount:
                # Not enough to gamble..
                message = ("@" + twitch_username + ", you do not have enough " +
                           currency_name + " to wager " + str(gambled_number) + " " + currency_name + ".")
            elif gambled_number < minimum_wager:
                message = ("@" + twitch_username + ", you must wager at least " +
                           str(minimum_wager) + " " + currency_name + ".")
            else:
                roll = random.randrange(lowest_possible_roll, highest_possible_roll + 1)
                message = twitch_username + " rolled a " + str(roll)
                # if roll == lowest_possible_roll:
                #       Rolled a 0..
                #     message += (". Timing you out for such a bad roll LUL. You also lost" +
                #                 str(gambled_number) + " " + currency_name + ".")
                #     mix_user = self.add_currency(mix_user_id, currency_id, gambled_number * -1)
                if roll <= 60:
                    # Loss
                    message += " and lost " + str(gambled_number) + " " + currency_name + "!"
                    mix_user = self.add_currency(mix_user_id, currency_id, gambled_number * -1)
                elif roll <= 97:
                    # x2 Win
                    message += " and won " + str(gambled_number*1) + " " + currency_name + "!"
                    mix_user = self.add_currency(mix_user_id, currency_id, gambled_number * 1)
                elif roll <= highest_possible_roll:
                    # x3 Win
                    message += " and won " + str(gambled_number*3) + " " + currency_name + " with a X3 WIN!"
                    mix_user = self.add_currency(mix_user_id, currency_id, gambled_number * 2)

            if mix_user is not None:
                # The currency addition was successful.
                currency_dictionary = mix_user['CurrencyAmounts'][0]
                currency_amount = currency_dictionary['Amount']
                currency_name = currency_dictionary['Name']
                message += " You now have " + str(currency_amount) + " " + currency_name + "."

        return message


if __name__ == "__main__":
    print('Running mix_it_up_extended.py as main method..')
    mix_client = MixClientExtended()
    pretty_print(mix_client.get_user("PanosXa"))
