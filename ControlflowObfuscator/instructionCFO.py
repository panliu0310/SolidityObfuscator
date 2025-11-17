import re

class instructionCFO:
	def __init__(self):
		# Match variable assignments like: variable = value;
        # - ([\w.]+): Matches variable names (e.g., `variable`, `obj.property`)
        # - \s*=\s*: Matches the equals sign with optional spaces around it
        # - (.*?);: Matches the value up to the semicolon (non-greedy)
		self.insertPattern = r'([\w.]+)\s*=\s*(.*?);'
		#self.pattern = r'(\w+\s*=\s*([^;]+));'
		self.replacePattern = r'(.*?)\s*^\s*(.*?);'
	
	def doInstructionInsert(self, _solContent):
		nowContent = _solContent
		nowContent = re.sub(self.insertPattern, r'\1 = \2 ^ 1 ^ 1;', nowContent)
		return nowContent
	
	#  a exclusive_or b ==> (a and not b) or (b and not a)
	def doInstructionReplace(self, _solContent):
		nowContent = _solContent
		nowContent = re.sub(self.replacePattern, r'(\1 && !\2) || (\2 && !\1)', nowContent)
		return nowContent
