#!/usr/bin/env python

# imports
import json
import requests
import sys
import time
import settings
import traceback
from datetime                          import datetime, timedelta
from operator                          import itemgetter
from os import remove
from beem.account                      import Account
from beem.amount                       import Amount
from beem.nodelist                     import NodeList
from beem                              import Steem
from beem.instance                     import set_shared_steem_instance
from apscheduler.schedulers.blocking   import BlockingScheduler
from tronapi import Tron
from tronapi import HttpProvider
from apscheduler.jobstores.sqlalchemy  import SQLAlchemyJobStore

# SQLite job store
jobstore = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
def balance_trx():
    balance = tron.trx.get_balance(is_float=True)
    return balance

def transfer_trx(to,amount):
    balance = balance_trx()
    if balance > amount:
        tron.trx.send_transaction(to,amount)

def sendEarnings():

    # Get the curation reward period
    today = datetime.utcnow()
    start_day = today - timedelta(hours=nhours)
    print('\n  --> The curation rewards will be tracked between ', start_day.strftime("%Y-%m-%d %H:%M:%S"), ' and ', today.strftime("%Y-%m-%d %H:%M:%S"))

    # Getting the information on the current delegators
    delegators = {}
    for op in account.history(only_ops=["delegate_vesting_shares",]):
        ## Security check
        if op["delegatee"] != account_name or op['delegator'] in list_accounts_ignore: 
            continue
        ## removing entries for removed delegations
        vesting_shares = op["vesting_shares"]["amount"]
        if vesting_shares == '0':
            if op['delegator'] in delegators.keys():
                del delegators[op['delegator']]
            continue
        ## For new delegation, the amount of shares is weighted proportionally to the period
        timestamp = datetime.strptime(op["timestamp"], '%Y-%m-%dT%H:%M:%S')
        timeweight =  min(nhours/24, (datetime.utcnow()-timestamp).total_seconds()/(86400.*float(nhours/24)))
        ## adding the delegator to the dictionary (or updating if already there)
        if op['delegator'] in delegators.keys() and float(vesting_shares)<delegators[op['delegator']]:
            delegators[op['delegator']] = float(vesting_shares)
        elif op['delegator'] in delegators.keys() and float(vesting_shares)>delegators[op['delegator']]:
            delegators[op['delegator']] = delegators[op['delegator']] + (float(vesting_shares)-delegators[op['delegator']])*timeweight
        else:
            delegators[op['delegator']] = float(vesting_shares)*timeweight
    delegators = sorted(delegators.items(), key=itemgetter(1), reverse=True)

    # Calculating the curation rewards in the period
    reward_vests = Amount("0 VESTS")
    for reward in account.history_reverse(only_ops=["curation_reward"], start=today, stop=start_day):
        reward_vests += Amount(reward['reward'])
    start_day = start_day.strftime("%Y-%m-%d %H:%M:%S")
    today     = today.strftime("%Y-%m-%d %H:%M:%S")
    print('Total curation rewards: ', round(stm.vests_to_sp(reward_vests.amount),5),' SP\n')

    fees = []
    cfees = []

    total_delegation = sum([x[1] for x in delegators])
    for delegator in delegators:
        delegator_fee = delegator[1]/total_delegation*delegator_share* \
            stm.vests_to_sp(reward_vests.amount)
        fees.append([delegator[0], round(float(delegator_fee),3)])

    total_fee = sum([x[1] for x in fees])

    curatorsReward = round(stm.vests_to_sp(reward_vests.amount),5) - round(total_fee,3)
    for curator in curators:
        curatorReward = curatorsReward/len(curators)
        cfees.append([curator,round(float(curatorReward),3)])

    print("\n  --> Redistributed rewards for delegators: ", str(round(total_fee,3)), " STEEM")
    if curators:
        print("  --> Redistributed rewards for curators: ", str(round(float(curatorsReward),3)), " STEEM\n")

    # Test Unit 3: Wallet size
    balance=float( paying_account.get_balances()['available'][0])
    if round(stm.vests_to_sp(reward_vests.amount),5)>balance:
        print('ERROR: Not enough money in the paying account wallet\n')
    elif rule_trx and round(stm.vests_to_sp(reward_vests.amount),5)>balance_trx():
        print('ERROR: Not enough TRX in the paying account wallet\n')
    else:
        
        # Payments
        print('List of delegators')
        for [k,v] in fees:
            if v>minimum_value_transfer:
                paying_account.transfer(k,v,'STEEM', cfg.delegators_memo%(str(start_day),str(today)))
                if rule_trx:
                    response = json.loads(requests.request("GET", "https://steemitwallet.com/api/v1/tron/tron_user?username=%s"%(k)).text)
                    if response["status"]=="ok" and response["result"]["tron_addr"]:
                        print('  ** ', k, ' will get ', v, ' SP and ',v,' TRX')
                        transfer_trx(response["result"]["tron_addr"],float(v))
                    else:
                        print('  ** ', k, ' will get ', v, ' SP')
                else:
                    print('  ** ', k, ' will get ', v, ' SP')
        if curators: 
            print('\nList of curators')
        for [k,v] in cfees:
            if v>minimum_value_transfer:
                paying_account.transfer(k,v,'STEEM', cfg.curators_memo%(str(start_day),str(today)))
                if rule_trx:
                    response = json.loads(requests.request("GET", "https://steemitwallet.com/api/v1/tron/tron_user?username=%s"%(k)).text)
                    if response["status"]=="ok" and response["result"]["tron_addr"]:
                        print('  ** ', k, ' will get ', v, ' SP and ',v,' TRX')
                        transfer_trx(response["result"]["tron_addr"],float(v))
                    else:
                        print('  ** ', k, ' will get ', v, ' SP')
                else:
                    print('  ** ', k, ' will get ', v, ' SP')
    print("--------------------------------------------------")
    print("  --> time the execution ended ",datetime.now())
    print("  --> time of next run ",datetime.now() + timedelta(hours=nhours))

if __name__ == '__main__':
    try:
        try:
            remove("jobs.sqlite")
        except Exception as e:    
            print("--------------------------------------------------")
        # Welcome message
        print("Start of the bot on:", time.asctime(time.localtime(time.time())))
        cfg = settings.Config()
        # Getting the active key of the paying account
        wif = cfg.wif
        payingAccount = cfg.payingAccount

        # Initialization of the Steem instance
        stm = Steem(node=cfg.list_nodes,keys=[wif])
        set_shared_steem_instance(stm)

        # Get the paying account
        paying_account  = Account(payingAccount, blockchain_instance=stm)
        if not paying_account:
            print('  --> Cannot get the paying account from the wif. Exiting.')
            print("End of the run on:", time.asctime(time.localtime(time.time())))
            sys.exit()
        else:
            print('  --> The paying account is ' + str(paying_account))


        # Get the delgated account
        account_name = cfg.account_name
        if not account_name:
            print('  --> Cannot get the account to track. Exiting.')
            print("End of the run on:", time.asctime(time.localtime(time.time())))
            sys.exit()
        else:
            print('  --> The delegated account is ' + account_name)
        account = Account(account_name)

        try:
            delegator_share = float(cfg.delegator_share)/100.
        except:
            print('  --> This should be a valued number')
            print("End of the run on:", time.asctime(time.localtime(time.time())))
            sys.exit()
        print('  --> ' + str(delegator_share) + ' of the curation rewards will be returned')

        # Test Unit 1: sanity
        # if not (delegator_share > 0 and delegator_share < 1): --- to force under 1%
        if not (delegator_share > 0 and delegator_share <= 1): 
            print('ERROR: cannot share more than 100% of all curation rewards\n')
            print("End of the run on:", time.asctime(time.localtime(time.time())))
            sys.exit()
        list_accounts_ignore = cfg.list_accounts_ignore
        minimum_value_transfer = cfg.minimum_value_transfer
        curators = cfg.curators
        if minimum_value_transfer <= 0.001:
            print('ERROR: Minimum value required for transfers must be greater than 0.001')
            sys.exit()
        nhours=cfg.hours

        # Trx data
        rule_trx= cfg.rule_trx
        if rule_trx:
            trx_public_key = cfg.trx_public_key
            trx_private_key = cfg.trx_private_key
            if not trx_public_key or not trx_private_key :
                print('  --> ')
                print("End of the run on:", time.asctime(time.localtime(time.time())))
                sys.exit()
            full_node = HttpProvider('https://api.trongrid.io')
            solidity_node = HttpProvider('https://api.trongrid.io')
            event_server = HttpProvider('https://api.trongrid.io')
            tron = Tron(full_node=full_node,
                        solidity_node=solidity_node,
                        event_server=event_server)
            tron.private_key = trx_private_key
            tron.default_address = trx_public_key
        # Starting the scheduler
        scheduler = BlockingScheduler(jobstores=jobstore)
        startday = datetime.now() + timedelta(hours=nhours)
        scheduler.add_job(sendEarnings, 'interval', hours=nhours, start_date=startday)

        print("The scheduler is now ready. First run is at %s" % str(startday) )
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("--------------------------------------------------")
        print("The bot has stopped.")
        try:
            remove("jobs.sqlite")
            print("The jobs.sqlite file was removed.")
        except FileNotFoundError:
            print("--------------------------------------------------")
        except PermissionError:
            print("ERROR: The jobs.sqlite file could not be removed")
        except Exception as e:    
            print("Error: The jobs.sqlite file could not be removed")
            print('Exception...', str(traceback.format_exc()))
