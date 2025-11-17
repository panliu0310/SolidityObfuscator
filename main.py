import sys

import layoutObfuscation
import dataflowObfuscation
import controlflowObfuscation

def main():
    print("Solidity obfuscation starts")
    #print("open {sys.argv[1]}")
    solContect = ""
    #with open(sys.argv[1], "r", encoding = "utf-8") as f:
    with open("FirstApp.sol", "r", encoding = "utf-8") as f:
        solContent = f.read()
    layoutObfuscation.layoutObfuscation(solContent)
    dataflowObfuscation.dataflowObfuscation(solContent)
    controlflowObfuscation.controlflowObfuscation(solContect)

def getContent(self, _filepath):
	with open(_filepath, "r", encoding = "utf-8") as f:
		return f.read()
	return str()

main()