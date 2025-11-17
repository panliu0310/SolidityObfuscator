from ControlflowObfuscator import instructionInsert

class controlflowObfuscation:

	def __init__(self, solContent):
		print("Initializing controlflow obfuscator")
		self.solContent = solContent
	
	def run(self):
		print("Start control flow confusion:")
		self.instructionInsert = instructionInsert.instructionInsert(self.solContent)
		self.solContent = self.instructionInsert.doInsert()
		print("Complete control flow confusion.")
		return self.solContent