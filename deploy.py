import json
import base64
from algosdk.v2client import algod
from algosdk import account, transaction , mnemonic
from algokit_utils import account as util_account





def fund_account(wallet_address:str , algod_client : algod.AlgodClient):

    try:
        
        # master_mnemonic = "toss transfer sure frozen real jungle mouse inch smoke derive floor alter ten eagle narrow perfect soap weapon payment chaos amateur height estate absent cabbage"
        # master_account = util_account.get_account_from_mnemonic(mnemonic=master_mnemonic)
        
        # master_wallet , master_private_key = master_account.address ,master_account.private_key

        master_account = util_account.get_localnet_default_account(client=algod_client)
        master_wallet , master_private_key = master_account.address , master_account.private_key



        params = algod_client.suggested_params()
        payment_txn = transaction.PaymentTxn(
            sender=master_wallet,
            sp=params,
            receiver=wallet_address,
            amt=1_000_000
        )

        signed_txn = payment_txn.sign(master_private_key)
        txid  = algod_client.send_transaction(txn=signed_txn)
        transaction.wait_for_confirmation(algod_client=algod_client , txid=txid)
        print("Fund successfull")
        return 1
    except Exception as e:
        print("Error :-" , e)
        return -1
    



def deploy_app(ARC32_FILE_PATH = "HelloWorld.arc32.json"):
    """Deploy the application using ARC-32 JSON"""

    # Testnet :- https://testnet-api.algonode.cloud/
    ALGOD_ADDRESS = "http://localhost:4001"
    ALGOD_TOKEN = "a" * 64

    
    # Algorand testnet client
    client  = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

    # Generate account
    private_key , wallet_address = account.generate_account()

    # Fund account
    is_funding_successfull = fund_account(wallet_address=wallet_address , algod_client=client)


    if is_funding_successfull == 1:
        try:
            # Read ARC-32 JSON file
            with open(ARC32_FILE_PATH, "r") as f:
                arc32_data = json.load(f)

            # Get the base64-encoded TEAL source from ARC-32
            approval_b64 = arc32_data['source']['approval']
            clear_b64 = arc32_data['source']['clear']

            # Decode base64 to get TEAL source code as strings
            approval_source = base64.b64decode(approval_b64).decode('utf-8')
            clear_source = base64.b64decode(clear_b64).decode('utf-8')

            # Compile the TEAL source to get bytecode
            approval_result = client.compile(approval_source)
            clear_result = client.compile(clear_source)
            
            # Convert base64-encoded compiled programs to bytes
            approval_program = base64.b64decode(approval_result['result'])
            clear_program = base64.b64decode(clear_result['result'])

            # Get suggested parameters
            params = client.suggested_params()

            # Define state schemas from ARC-32
            global_schema = transaction.StateSchema(
                num_uints=arc32_data['state']['global'].get('num_uints', 0),
                num_byte_slices=arc32_data['state']['global'].get('num_byte_slices', 0)
            )
            local_schema = transaction.StateSchema(
                num_uints=arc32_data['state']['local'].get('num_uints', 0),
                num_byte_slices=arc32_data['state']['local'].get('num_byte_slices', 0)
            )

            # Create application transaction
            txn = transaction.ApplicationCreateTxn(
                sender=wallet_address,
                sp=params,
                on_complete=transaction.OnComplete.NoOpOC,
                approval_program=approval_program,  # Now bytes
                clear_program=clear_program,       # Now bytes
                global_schema=global_schema,
                local_schema=local_schema
            )

            # Sign and send transaction
            signed_txn = txn.sign(private_key)
            tx_id = client.send_transaction(signed_txn)
            
            # Wait for confirmation
            confirmed_txn = transaction.wait_for_confirmation(client, tx_id, 4)
            app_id = confirmed_txn['application-index']
            return {
                "transaction_id" : tx_id,
                "app_id":app_id,
                "wallet_address":wallet_address,
                "private_key" : private_key
            }

        except Exception as e:
            print(f"Error deploying application: {str(e)}")
            return None
    else:
        print("Account funding Failed :( try again !!!")
        return -1

if __name__ == "__main__":
    deploy_app()