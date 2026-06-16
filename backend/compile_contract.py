import json
from solcx import compile_source, install_solc

def compile_contract():
    # Install the solidity compiler version matching the contract
    install_solc('0.8.20')
    
    with open('app/contracts/AttendanceAudit.sol', 'r') as f:
        contract_source = f.read()

    compiled_sol = compile_source(
        contract_source,
        output_values=['abi', 'bin'],
        solc_version='0.8.20'
    )
    
    # Retrieve the contract interface
    contract_id, contract_interface = compiled_sol.popitem()
    
    abi = contract_interface['abi']
    bytecode = contract_interface['bin']

    output = {
        "abi": abi,
        "bytecode": bytecode
    }
    
    with open('app/contracts/AttendanceAudit.json', 'w') as f:
        json.dump(output, f, indent=4)
        
    print("Contract compiled successfully to app/contracts/AttendanceAudit.json")

if __name__ == '__main__':
    compile_contract()
