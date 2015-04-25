import grammar
from grako.ast import AST

def entity(type):
	def sub(func, *args, **kwargs):
		def subsub(self, ast, *args, **kwargs):
			ast['entity'] = type
			ret = func(self, ast, *args, **kwargs)
			return ast if ret is None else ret
		return subsub
	return sub

class Semantics(object):
	def _default(self, ast, *args, **kwargs):
		if isinstance(ast, AST) and 'rule' not in ast:
			ast['rule'] = ast._parseinfo.rule
		return ast
	def tokString(self, ast):
		return dict(chars=''.join(ast), rule='tokString')
	def listJoiner(self, ast):
		return [ast[0]] + ast[1]
	valueListNE = listJoiner
	dagArgList = listJoiner
	templateArgList = listJoiner
	baseClassListNE = listJoiner

if __name__=='__main__':
	import sys, pprint
	with open(sys.argv[1]) as f:
		text = f.read()
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
	pprint.pprint(flatten(ast))
