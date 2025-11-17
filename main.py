import os
import sys

import layoutObfuscation
import dataflowObfuscation
import controlflowObfuscation

def main():
    print("Solidity obfuscation starts")
    
    solContent = ""
    #input = sys.argv[1]
    input = "FirstApp.sol"
    #output = sys.argv[2]
    output = "output.sol"
    
    if not os.path.exists(input):
        raise FileNotFoundError(f"File '{input}' does not exist.")
    #print("open {sys.argv[1]}")
    #with open(sys.argv[1], "r", encoding = "utf-8") as f:
    with open(input, "r", encoding = "utf-8") as f:
        solContent = f.read()
    
    #dataflowObfuscation.dataflowObfuscation(solContent)
    #controlflowObfuscation.controlflowObfuscation(solContect)
    #layoutObfuscation.layoutObfuscation(solContent)

    try:
        with open(output, 'w', encoding='utf-8') as file:
            file.write(solContent)
        print(f"File saved successfully: {output}")
    except Exception as e:
        raise IOError(f"Failed to save file at {output}: {e}")

main()