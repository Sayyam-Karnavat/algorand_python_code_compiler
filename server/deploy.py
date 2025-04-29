import algokit_utils
import os
from dotenv import load_dotenv
from algosdk import account , mnemonic
import algokit_utils
from algokit_utils import OnUpdate, OnSchemaBreak  , PaymentParams , AlgoAmount 
import re
import subprocess
import json
import shutil
import tempfile
import sys


os.environ["PATH"] = f"{os.environ.get('PATH')}:{os.path.expanduser('~/.local/bin')}"

load_dotenv()





def fund(address):
    try:
        algorand = algokit_utils.AlgorandClient.testnet()
        dispenser = algorand.client.get_testnet_dispenser(auth_token=os.getenv("DISPENSER_TOKEN"))
        dispenser.fund(address=address , amount=1_000_000)

        algorand.account.ensure_funded_from_testnet_dispenser_api(
            account_to_fund=address,
            dispenser_client=dispenser,
            min_spending_balance=algokit_utils.AlgoAmount(algo=1)
        )
        return True
    except Exception as e :
        return {
            "error" : str(e)
        }
    

def fund_from_private_Account(receiver_address):
    try:

        algorand_client = algokit_utils.AlgorandClient.testnet()

        master_mnemonic = os.getenv("DEPLOYER")

        master_account = algorand_client.account.from_mnemonic(mnemonic=master_mnemonic)

        result = algorand_client.send.payment(
            PaymentParams(
                sender=master_account.address,
                receiver=receiver_address,
                amount=AlgoAmount(algo=2),  # Sending 1 Algo
                signer=master_account.signer,
                note=b"Payment transaction example"  # Optional note
            )
        )
        return True
    except Exception as e :
        return {
            "error" : str(e)
        }



def compile(smart_contract_code):
    def extract_class_name(code):
        # Look for class definitions that inherit from ARC4Contract
        match = re.search(r'class\s+(\w+)\s*\(\s*ARC4Contract\s*\)', code)
        return match.group(1) if match else None

    try:
        # Validate input
        if not isinstance(smart_contract_code, str) or not smart_contract_code.strip():
            return {"error": "Invalid or empty smart contract code"}

        # Extract the contract class name
        contract_name = extract_class_name(smart_contract_code)
        if not contract_name:
            return {"error": "Could not extract contract class name. Ensure the code defines a class inheriting from ARC4Contract"}

        # Create a temporary directory in /tmp (safe for Vercel)
        temp_dir = tempfile.mkdtemp(dir='/tmp' if os.path.exists('/tmp') else None)

        
        # Write the smart contract code to a temporary .py file
        temp_file_path = os.path.join(temp_dir, f"{contract_name}.py")
        with open(temp_file_path, "w") as f:
            f.write(smart_contract_code)

        # Expected output JSON file path
        json_file_path = os.path.join(temp_dir, f"{contract_name}.arc56.json")
        

        possible_paths = [
        os.path.join(sys.prefix, 'bin', 'algokit'),  # Standard pip install location
        os.path.join(os.path.expanduser('~'), '.local', 'bin', 'algokit'),  # User install location
        '/var/task/.local/bin/algokit'  # Common Vercel location
    ]
        algokit_path = None
        for path in possible_paths:
            if os.path.exists(path):
                algokit_path = path
                break

        
        if algokit_path:
            full_command = [algokit_path] + command
        
        else:

            # Compile the contract with algokit
            command = [
                "algokit", "compile", "python", temp_file_path, "--output-arc56", "--no-output-teal", "--out-dir", temp_dir
            ]


        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )
        
        # Check for command failure
        if result.returncode != 0:
            return {
                "error": f"Compilation failed: {result.stderr}",
                "stdout": result.stdout
            }

        # Check if the JSON file was created
        if not os.path.exists(json_file_path):
            return {
                "error": f"Compiled JSON file not found. Check if algokit generated the output.",
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        # Read the JSON content
        with open(json_file_path, "r") as f:
            json_content = json.load(fp=f)

        # Return the JSON content
        return {
            "success": True,
            "json_content": json_content
        }
        # Clean up: Remove the temporary directory and all its contents
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    except Exception as e:
        return {"success": False , "json_content" : {} , "error" : str(e)}
    


def deploy_app(smart_contract_code):
    try:

        private_key , address = account.generate_account()
        user_mnemomic = mnemonic.from_private_key(private_key)
        

        algorand = algokit_utils.AlgorandClient.testnet()
        deployer = algorand.account.from_mnemonic(mnemonic=user_mnemomic)

        
        # Algokit testnet dispenser limit exceeded
        # fund_response = fund(address=address)


        # Hence funding from private account
        private_fund_response=fund_from_private_Account(receiver_address=address)

        


        
        if private_fund_response != True:
            return {
                "error" : private_fund_response['error']
            }


        compile_response = compile(smart_contract_code=smart_contract_code)

        

        if compile_response['success'] == True and compile_response['json_content']:

            app_spec = compile_response['json_content']

        else:
            return compile_response
        
        
        factory = algorand.client.get_app_factory(
        
        app_spec=app_spec,
            default_sender=deployer.address
        )


        


        # Deploy the application
        app_client, deploy_response = factory.deploy(
            on_update=OnUpdate.AppendApp, # Create a new app if updating
            on_schema_break=OnSchemaBreak.AppendApp, # Create a new app if schema breaks
            compilation_params={
            "deploy_time_params": {"VERSION": 1}, # Optional template parameters
            },
        )

        
        
        algorand.send.payment(
            algokit_utils.PaymentParams(
            amount=algokit_utils.AlgoAmount(algo=1),
            sender=deployer.address,
            receiver=app_client.app_address,
            )
        )
        return {
            "private_key" : private_key,
            "wallet_address" : address,
            "deployed_app_id" : app_client.app_id,
        }
    except Exception as e:
        return {
            "error" : str(e)
        }

