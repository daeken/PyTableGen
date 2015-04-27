import grammar
from grako.ast import AST

class Semantics(object):
	def _default(self, ast, *args, **kwargs):
		if isinstance(ast, AST) and 'rule' not in ast:
			ast['rule'] = ast._parseinfo.rule
		return ast
	def tokString(self, ast):
		return ''.join(ast)
	def listJoiner(self, ast):
		return [ast[0]] + ast[1]
	def stringJoin(self, ast):
		return dict(chars=''.join(ast), rule='tokString')
	valueListNE = listJoiner
	dagArgList = listJoiner
	templateArgList = listJoiner
	baseClassListNE = listJoiner

def parse(text):
	parser = grammar.grammarParser(parseinfo=True)
	ast = parser.parse(
		text,
		'tableGenFile',
		filename=sys.argv[1],
		trace=False, 
		semantics=Semantics())
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
	pprint.pprint(parse(text))
