import json
import base64
from algosdk.v2client import algod
from algosdk import account, transaction
from algokit_utils import account as util_account

# Constants
ALGOD_ADDRESS = "http://localhost:4001"
ALGOD_TOKEN = "a" * 64
ARC32_FILE_PATH = "HelloWorld.arc32.json"


def get_client():
    """Initialize and return Algod client"""
    return algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def deploy_app(client, private_key, wallet_address):
    """Deploy the application using ARC-32 JSON"""
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
        
        print(f"Transaction ID: {tx_id}")
        print(f"Application ID: {app_id}")
        return app_id

    except Exception as e:
        print(f"Error deploying application: {str(e)}")
        return None

if __name__ == "__main__":
    # Initialize client
    algod_client = get_client()
    
    # Get account
    localnet_account = util_account.get_localnet_default_account(client=algod_client)
    private_key = localnet_account.private_key
    wallet_address = localnet_account.address
    
    # Deploy the application
    app_id = deploy_app(algod_client, private_key, wallet_address)