import grammar
from grako.ast import AST

class Semantics(object):
	def _default(self, ast, *args, **kwargs):
		if isinstance(ast, AST) and 'rule' not in ast:
			ast['rule'] = ast._parseinfo.rule
		return ast
	def tokString(self, ast):
		return u''.join(ast)
	def listJoiner(self, ast):
		return [ast[0]] + ast[1]
	def stringJoin(self, ast):
		return dict(value=u''.join(ast), rule='tokString')
	valueListNE = listJoiner
	dagArgList = listJoiner
	templateArgList = listJoiner
	baseClassListNE = listJoiner

	def decimalInteger(self, ast):
		if isinstance(ast, list):
			return int(''.join(ast))
		return {'rule' : 'tokInteger', 'value': int(ast)}
	def hexInteger(self, ast):
		return {'rule' : 'tokInteger', 'value': int(ast, 16)}
	def binInteger(self, ast):
		return {'rule' : 'tokInteger', 'value': int(ast, 2)}

def parse(filename, text):
	parser = grammar.grammarParser(parseinfo=True)
	ast = parser.parse(
		text,
		'tableGenFile',
		filename=filename,
		trace=False, 
		semantics=Semantics(), 
		comments_re=r'\s*(//.*$|/\*(.|\n)*?\*/)')
	def flatten(ast):
		if isinstance(ast, list):
			return map(flatten, ast)
		elif isinstance(ast, AST):
			return {k:flatten(v) for k, v in ast.items()}
		else:
			return ast
	return flatten(ast)	

if __name__=='__main__':
	import sys, pprint
	with open(sys.argv[1]) as f:
		text = f.read()
	pprint.pprint(parse(sys.argv[1], text))
