from ControlflowObfuscator import instructionCFO

class controlflowObfuscation:

	def __init__(self, solContent):
		print("Initializing controlflow obfuscator")
		self.solContent = solContent
	
	def run(self):
		print("Start control flow confusion:")
		self.instructionCFO = instructionCFO.instructionCFO()
		self.solContent = self.instructionCFO.doInstructionInsert(self.solContent)
		self.solContent = self.instructionCFO.doInstructionReplace(self.solContent)

		print("Complete control flow confusion.")
		return self.solContent