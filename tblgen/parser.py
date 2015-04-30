import grammar, sys
from grako.exceptions import FailedParse
from grako.ast import AST

includePaths = ['.']
included = []

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
	rangeList = listJoiner

	def decimalInteger(self, ast):
		if isinstance(ast, list):
			return int(''.join(ast))
		return {'rule' : 'tokInteger', 'value': int(ast)}
	def hexInteger(self, ast):
		return {'rule' : 'tokInteger', 'value': int(ast, 16)}
	def binInteger(self, ast):
		return {'rule' : 'tokInteger', 'value': int(ast, 2)}

	def includeDirective(self, ast):
		print >>sys.stderr, 'Including', ast
		if ast in included:
			return None
		included.append(ast)
		for dir in includePaths:
			try:
				fn = dir + '/' + ast
				return parse(fn)
			except IOError:
				pass
			except FailedParse:
				import traceback
				traceback.print_exc()
				raise
		print 'Could not find include file:', ast
		print 'Include paths:', includePaths
		assert False

def parse(filename, _includePaths=None):
	global includePaths
	if _includePaths is None:
		_includePaths = []
	if '/' in filename:
		_includePaths.append(filename.rsplit('/', 1)[0])
	for elem in _includePaths:
		if elem not in includePaths:
			includePaths.append(elem)
	parser = grammar.grammarParser(parseinfo=True)
	with open(filename) as f:
		text = f.read()
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
	import pprint
	pprint.pprint(parse(sys.argv[1]))
