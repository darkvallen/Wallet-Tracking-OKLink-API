import requests
import json
from prettytable import PrettyTable

ADDRESS = "DESIRED_WALLET_ADDRESS"  # Replace with the wallet address to analyze
API_KEY = "YOUR_OKLINK_API_KEY"  # Replace with your OkLink API key 

#Fetches a list of chains where the given wallet address has been active.
def get_active_chains(ADDRESS):

    url = "https://www.oklink.com/api/v5/explorer/address/address-active-chain"
    headers = {
        "Ok-Access-Key": API_KEY,
        "Content-type": "application/json"
    }
    params = {
        "address": ADDRESS
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json().get('data', [])
    if response.status_code == 200:
        active_chains = [] 

        if data:
            table = PrettyTable(["Chain Fullname", "Chain Shortname"])
            for item in data:  
                table.add_row([item['chainFullName'], item['chainShortName']])
                active_chains.append(item['chainShortName']) 
            print(table)
        else:
            print("No data found.")
    else:
        print(f"Error fetching data: {response.status_code}")
    return active_chains

#Gets the balance of the native token for a specified address and chain.
def get_native_token_balance(ADDRESS, chain_short_name):
    url = f"https://www.oklink.com/api/v5/explorer/address/address-summary"
    params = {
        "chainShortName": chain_short_name,
        "address": ADDRESS
    }
    headers = {
        "Ok-Access-Key": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            balance_data = data[0]
            balance = balance_data["balance"]
            balance_symbol = balance_data["balanceSymbol"]
            totaltokenval = balance_data["totalTokenValue"]
            print(f"Native token balance on {chain_short_name}: {balance} {balance_symbol}")
        else:
            print(f"No data found for {ADDRESS} on {chain_short_name}")
    else:
        print(f"Error fetching data: {response.status_code}")

#Fetches token details (e.g., market cap, trading volume) for a given token contract address.
def get_token_data(chain_short_name, token_contract_address):
    url = f"https://www.oklink.com/api/v5/explorer/token/token-list"
    params = {
        "chainShortName": chain_short_name,
        "tokenContractAddress": token_contract_address,
        "limit": 1
    }
    headers = {
        "Ok-Access-Key": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            token_info = data[0].get('tokenList', [{}])[0]  
            return token_info
        else:
            print(f"No token data found for {token_contract_address} on {chain_short_name}")
    else:
        print(f"Error fetching token data: {response.status_code}")
    print(response.json)

#Gets ERC-20 token balances for a specified address and chain.
def get_erc20_balances(ADDRESS, chain_short_name):
    url = f"https://www.oklink.com/api/v5/explorer/address/token-balance"
    params = {
        "chainShortName": chain_short_name,
        "address": ADDRESS,
        "protocolType": "token_20",
        "limit":"50"
    }
    headers = {
        "Ok-Access-Key": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            token_list = data[0].get("tokenList", [])  
            return token_list  
        else:
            print(f"No ERC-20 token data found for {ADDRESS} on {chain_short_name}")
    else:
        print(f"Error fetching ERC-20 token data: {response.status_code}")
    
#Retrieves NFT holdings of an address on a supported chain.        
def get_nft_holding(ADDRESS, chain_short_name):

    url = f"https://www.oklink.com/api/v5/explorer/{chain_short_name}/api?module=account&action=addresstokennftbalance&address={ADDRESS}&offset=100"
    headers = {
        "Ok-Access-Key": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        nft_list = response.json().get("result", [])
        if nft_list:
            return nft_list  
    else:
        print(f"Error fetching NFT data: {response.status_code}")

#Fetches address labels (if any).
def get_address_label(ADDRESS):

    url = f"https://www.oklink.com/api/v5/explorer/address/entity-label"
    headers = {
        "Ok-Access-Key": API_KEY,
        "Content-type": "application/json"
    }
    params = {
        "chainShortName": "eth",
        "address": ADDRESS,     
    }
    response = requests.get(url, headers=headers,params=params)
    
    if response.status_code == 200:
        data = response.json().get("data", [])
        if data:
            labels = data[0].get('label', '')
            return labels
        else:
            return ""
    else:
        print(f"Error fetching address label: {response.status_code}")
        return "Error"

#Retrieves recent transactions for a given address and chain.
def get_recent_transactions(ADDRESS, chain_short_name, limit):
    url = f"https://www.oklink.com/api/v5/explorer/address/transaction-list"
    params = {
        "chainShortName": chain_short_name,
        "address": ADDRESS,
        "limit": limit
    }
    headers = {
        "Ok-Access-Key": API_KEY,
        "Content-Type": "application/json"
    }

    all_transactions = []
    current_page = 1

    while True:
        params['page'] = current_page
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                transactions = data[0].get('transactionLists', [])
                all_transactions.extend(transactions)
                current_page += 1
                if len(transactions) < limit:  # Stop if fewer transactions are returned
                    break
            else:
                break  # No more transaction data
        else:
            print(f"Error fetching transactions: {response.status_code}")
            break
    return all_transactions

#Analyze transaction data to find frequently interacting addresses.
def analyze_transactions(transactions):
    counter = {}
    for tx in transactions:
        for address in [tx['from'], tx['to']]:
            if address != ADDRESS:  # Exclude the main address being analyzed
                counter[address] = counter.get(address, 0) + 1

    sorted_addresses = sorted(counter.items(), key=lambda item: item[1], reverse=True)
    return sorted_addresses

def main():

    print("[Wallet Address]\n")
    print(f"{ADDRESS}\n")
    print(f"[Address Active Chain]\n")
    active_chains = get_active_chains(ADDRESS)
    for chain_short_name in active_chains:  # Iterate directly over chain_short_name
        print(f"\n[Token Holding On {chain_short_name}]\n")
        try:
            balance_data = get_native_token_balance(ADDRESS, chain_short_name)
            if balance_data:
                print(f"Native token balance for {chain_short_name}: {balance_data['balance']} {balance_data['balanceSymbol']}")
        except Exception as e:
            print(f"Error getting balance for {chain_short_name}: {e}")  
        try:
            erc20_tokens = get_erc20_balances(ADDRESS, chain_short_name)
            if erc20_tokens:
                print(f"ERC-20 Tokens on {chain_short_name}:")
                total_value = 0.0
                for token in erc20_tokens:
                    print(f"  - {token['symbol']}: {token['holdingAmount']}") 
                    if token['valueUsd'] :
                        print(f"     - Token Holding Value(USD) : {token['valueUsd']}")
                        total_value += float(token['valueUsd']) 
                    token_data = get_token_data(chain_short_name, token['tokenContractAddress'])
                    if token_data:
                        token['marketCap'] = token_data.get('totalMarketCap')
                        token['tradingVolume24h'] = token_data.get('transactionAmount24h')
                    if token['marketCap']:
                        print(f"     - Total Market Cap : {token.get('marketCap')}")  # Display additional data
                    if token['tradingVolume24h']:
                        print(f"     - 24-Hour Trading Volume : {token.get('tradingVolume24h')}")
                print(f"Total ERC-20 Tokens value on {chain_short_name}: {total_value} USD")
        
        except Exception as e:
            print(f"Error getting ERC-20 tokens for {chain_short_name}: {e}") 
        try:
            supported_chains = ["ETH", "POLYGON", "XLAYER", "XLAYER_TESTNET", "OP", "SCROLL", "ZKSYNC", "POLYGON_ZKEVM", "MANTA", "CANTO"]
            if chain_short_name in supported_chains:
                print(f"\n[NFT Holding On {chain_short_name}]\n")
                nft_holding = get_nft_holding(ADDRESS, chain_short_name)
                if nft_holding:  
                    for nft in nft_holding:
                        print(f"  - {nft['TokenName']}: {nft['TokenQuantity']}") 
                else:
                    print(f"No NFTs found on {chain_short_name}")  
        except Exception as e:
            print(f"Error getting NFT for {chain_short_name}: {e}") 
        
    transactions = get_recent_transactions(ADDRESS, "eth",50)
    if transactions:
        frequent_addresses = analyze_transactions(transactions)
        print("\n[Top Interacting Addresses on ETH Chain]")
        for address, count in frequent_addresses[:5]:  # Print top 5
            label = get_address_label(address) 
            if label:
                print(f"  - {address} ({label}) : {count} interactions")
            else:
                print(f"  - {address} : {count} interactions")

if __name__ == "__main__":
    main()
