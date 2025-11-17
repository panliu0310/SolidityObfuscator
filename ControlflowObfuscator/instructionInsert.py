import re

class instructionInsert:
	def __init__(self, _solContent):
		self.content = _solContent
		# Match variable assignments like: variable = value;
        # - ([\w.]+): Matches variable names (e.g., `variable`, `obj.property`)
        # - \s*=\s*: Matches the equals sign with optional spaces around it
        # - (.*?);: Matches the value up to the semicolon (non-greedy)
		self.pattern = r'([\w.]+)\s*=\s*(.*?);'
		#self.pattern = r'(\w+\s*=\s*([^;]+));'
	
	def doInsert(self):
		nowContent = self.content
		nowContent = re.sub(self.pattern, r"\1 = \2 ^ 1 ^ 1;", nowContent)
		return nowContent