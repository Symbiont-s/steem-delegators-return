'''
        The settings file for the bot.
'''

class Config:

    def __init__(self):

        # Ignore the TRX to send the profits (true/false)
        self.rule_trx=True

        # Active key of the payment account
        self.wif = ""
        
        # Name of the payment account
        self.payingAccount = "ecosynthesizer"

        # The account from which delegations must be tracked
        self.account_name = "ecosynthesizer"

        # Percentage of the curation reward to send back. Allow it to be more than 100%. 
        self.delegator_share = 60

        # Minimum value required for transfers.  [Must be greater than 0.001]
        self.minimum_value_transfer = 0.01

        # Steem RPC
        self.list_nodes =["https://api.steemit.com"]

        # Lists accounts to ignore when distributing the rewards
        self.list_accounts_ignore = [""]

        # TRON public key
        self.trx_public_key = ''

        # TRON private key
        self.trx_private_key = ''

        # Calculate and distribute the rewards every x hours.
        self.hours = 24

        # List of curators to be rewarded (Leaving the list empty is equivalent to disabling this functionality)
        self.curators = ["dr-frankenstein"]

        # Delegators memo
        self.delegators_memo = "Ecosynthesizer Delegation tip [%s -- %s]"

        # Curators memo
        self.curators_memo = "Ecosynthesizer Curator tip [%s -- %s]"
