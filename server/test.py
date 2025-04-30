import requests


with open("contract.py" , "r") as f:
    contract_code = f.read()    


temp_json = {
    "code" : contract_code
}

response = requests.post(url="https://algorand-python-code-compiler.onrender.com/deploy" , json=temp_json)


print(response.text)