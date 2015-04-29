import grammar
from grako.ast import AST

includePaths = ['.']

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
	letList = listJoiner

	def decimalInteger(self, ast):
		if isinstance(ast, list):
			return int(''.join(ast))
		return {'rule' : 'tokInteger', 'value': int(ast)}
	def hexInteger(self, ast):
		return {'rule' : 'tokInteger', 'value': int(ast, 16)}
	def binInteger(self, ast):
		return {'rule' : 'tokInteger', 'value': int(ast, 2)}

	def includeDirective(self, ast):
		for dir in includePaths:
			try:
				fn = dir + '/' + ast
				with open(fn) as f:
					return parse(ast, f.read())
			except IOError:
				pass
		print 'Could not find include file:', ast
		print 'Include paths:', includePaths
		assert False

def parse(filename, text, _includePaths=None):
	global includePaths
	if _includePaths is None:
		_includePaths = []
	if '/' in filename:
		_includePaths.append(filename.rsplit('/', 1)[0])
	for elem in _includePaths:
		if elem not in includePaths:
			includePaths.append(elem)
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
