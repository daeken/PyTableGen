from parser import parse
from pprint import pprint
from collections import OrderedDict
import itertools, re

class TableGenType(object):
	def __init__(self, type):
		self.type = type

	def __str__(self):
		return str(self.type)

	@staticmethod
	def cast(type):
		if isinstance(type, unicode):
			return TableGenType(type)
		elif type['rule'] == 'listType':
			return TableGenList(TableGenType.cast(type['type']))
		elif type['rule'] == 'bitsType':
			return TableGenBits(type['width']['value'])
		else:
			print 'Unknown rule for TableGenType:', type['rule']
			pprint(type)
			assert False

class TableGenList(TableGenType):
	def __str__(self):
		return 'list<%s>' % self.type

class TableGenBits(TableGenType):
	def __init__(self, width):
		self.type = 'bits'
		self.width = width

	def __str__(self):
		return 'bits<%i>' % self.width

class Definitions(list):
	def deriving(self, cls):
		return Definitions([tdef for tdef in self if cls in tdef[1][0]])

	def named(self, name):
		return [tdef for tdef in self if tdef[0] == name][0]

class Definition(OrderedDict):
	def __getattr__(self, name):
		if name in self:
			return self[name]
		else:
			return OrderedDict.__getattr__(self, name)

class Dag(object):
	def __init__(self, interpreter, elem):
		self.elements = []
		for elem in [elem['root']] + ([] if elem['args'] is None else elem['args']):
			self.elements.append((elem['name'], interpreter.evalexpr(elem['value'])))

	def __repr__(self):
		return 'Dag(%s)' % (', '.join('%s:%s' % (value, name) if name is not None else str(value) for name, value in self.elements))

class Interpreter(object):
	def __init__(self, ast):
		self.ast = ast

		self.classes = {}
		self.multiclasses = {}

		self.anony_i = 0
		self.basenames = []
		self.contexts = []
		self.context = {}
		self.lets = []
		self.let = {}
		self.cur_def = None
		self.defs = Definitions()

		self.define(ast)
		self.execute(ast)

	def define(self, elem):
		if isinstance(elem, dict):
			assert 'rule' in elem
			if elem['rule'] == 'tclass':
				body = elem['body'] if elem['body'] != ';' else []
				body = self.let.values() + body
				self.classes[elem['name']] = dict(
					name=elem['name'],
					bases=elem['bases'] if elem['bases'] is not None else [],  
					args=elem['args'] if elem['args'] is not None else [], 
					body=body
				)
			elif elem['rule'] == 'multiClass':
				body = elem['body'] if elem['body'] != ';' else []
				body = self.let.values() + body
				self.multiclasses[elem['name']] = dict(
					name=elem['name'],
					bases=elem['bases'] if elem['bases'] is not None else [],  
					args=elem['args'] if elem['args'] is not None else [], 
					body=body
				)
			elif elem['rule'] == 'let':
				self.pushlet()
				for item in elem['items_']:
					assert item['rule'] == 'letItem'
					item['rule'] = 'bodyLet'
					self.let[item['name']] = item
				self.define(elem['body'])
				self.poplet()
			elif elem['rule'] not in ('tdef', 'defm'):
				print 'Unhandled rule:', elem['rule']
				assert False
		elif isinstance(elem, list):
			map(self.define, elem)
		else:
			print 'Unknown element:', 
			pprint(elem)
			assert False

	def execute(self, elem):
		if isinstance(elem, dict):
			assert 'rule' in elem
			if elem['rule'] == 'tdef':
				self.pushcontext()
				if elem['name'] is None:
					cname = 'anonymous_%i' % (self.anony_i)
					self.anony_i += 1
				else:
					cname = elem['name']
				if 'NAME' in self.context:
					NAME = self.context['NAME']
					while True:
						if cname.startswith('NAME#'):
							cname = NAME + cname[5:]
						elif cname.endswith('#NAME'):
							cname = cname[:-5] + NAME
						elif '#NAME#' in cname:
							cname = cname.replace('#NAME#', NAME)
						else:
							break
				if cname == elem['name']:
					cname = u''.join(self.basenames) + elem['name']
				if len(self.basenames) == 0:
					self.context['NAME'] = cname
				self.cur_def = ([], Definition(NAME=('string', self.context['NAME'])))
				self.defs.append((cname, self.cur_def))
				if elem['bases'] is not None:
					for cls in elem['bases']:
						self.evalclass(cls['id'], cls['args'])
				if len(self.basenames) > 0:
					self.cur_def[0].append(elem['name'])
				if elem['body'] != ';':
					self.evalbody(elem['body'])
				self.popcontext()

				return cname
			elif elem['rule'] == 'defm':
				self.pushcontext()
				if elem['name'] is None:
					name = 'anonymous_%i' % (self.anony_i)
					self.anony_i += 1
				else:
					name = elem['name']
				if 'NAME' not in self.context:
					self.context['NAME'] = name
				self.basenames.append(name)
				if elem['bases'] is not None:
					for cls in elem['bases']:
						self.evalclass(cls['id'], cls['args'])
				self.basenames.pop()
				self.popcontext()
			elif elem['rule'] == 'let':
				self.pushlet()
				for item in elem['items_']:
					assert item['suffix'] is None
					self.let[item['name']] = self.evalexpr(item['value'])
				self.execute(elem['body'])
				self.poplet()
			elif elem['rule'] not in ('tclass', 'multiClass'):
				print 'Unhandled rule:', elem['rule']
				assert False
		elif isinstance(elem, list):
			return map(self.execute, elem)
		else:
			print 'Unknown element:', 
			pprint(elem)
			assert False

	def handleargs(self, clsargs, args):
		if args is None:
			args = []
		numoptional = len([arg['value'] is not None for arg in clsargs])
		assert len(clsargs) >= len(args) >= len(clsargs) - numoptional
		for i, elem in enumerate(clsargs):
			if len(args) > i:
				self.context[elem['name']] = self.evalexpr(args[i])
			else:
				self.context[elem['name']] = self.evalexpr(clsargs[i]['value'])

	def evalclass(self, name, args):
		if name in self.multiclasses:
			self.evalmulticlass(name, args)
			return

		cls = self.classes[name]
		self.handleargs(cls['args'], args)

		for base in cls['bases']:
			self.evalclass(base['id'], base['args'])

		self.cur_def[0].append(name)

		self.evalbody(self.classes[name]['body'])

	def evalmulticlass(self, name, args):
		mcls = self.multiclasses[name]

		self.handleargs(mcls['args'], args)

		self.execute(mcls['body'])

	def evalbody(self, body):
		for elem in body:
			if elem['rule'] == 'declaration':
				val = self.evalexpr(elem['value'])
				type = TableGenType.cast(elem['type'])
				if elem['name'] in self.let:
					val = self.let[elem['name']]
				self.cur_def[1][elem['name']] = (type, val)
				self.context[elem['name']] = val
			elif elem['rule'] == 'bodyLet':
				val = self.evalexpr(elem['value'])
				assert elem['name'] in self.cur_def[1]
				assert elem['suffix'] is None
				type = self.cur_def[1][elem['name']][0]
				self.let[elem['name']] = val
				self.cur_def[1][elem['name']] = (type, val)
				self.context[elem['name']] = val
			else:
				print 'Unknown element in body:', elem['rule']
				assert False

	def evalexpr(self, value):
		if value is None:
			return None
		if value['rule'] == 'value':
			value, suffixes = value['value'], value['suffixes']
			if isinstance(value, dict):
				if value['rule'] in ('tokString', 'tokInteger'):
					value = value['value']
				elif value['rule'] == 'bangValue':
					value = self.evalbang(value['operator'], map(self.evalexpr, value['args']))
				elif value['rule'] == 'simpleList':
					assert value['type'] is None
					value = map(self.evalexpr, value['values_']) if value['values_'] is not None else []
				elif value['rule'] == 'dag':
					value = Dag(self, value)
				elif value['rule'] == 'tokCodeFragment':
					value = ('code', value['fragment'])
				elif value['rule'] == 'implicitDef':
					cur_def = self.cur_def
					basenames = self.basenames
					self.basenames = []
					tdef = dict(
						rule='tdef', 
						name=None, 
						bases=[value],
						body=';'
					)
					value = ('defref', self.execute(tdef))
					self.cur_def = cur_def
					self.basenames = basenames
				else:
					print 'Unknown value in expr:', value['rule']
					pprint(value)
					assert False
			elif isinstance(value, unicode):
				if value == '?':
					value = None
				elif value in self.context:
					value = self.context[value]
				elif value in [cdef[0] for cdef in self.defs]:
					value = ('defref', value)
				else:
					print 'Unknown name:', value
					assert False
			elif isinstance(value, int):
				pass
			else:
				print 'Unknown value in expr'
				pprint(value)
				assert False

			for suffix in suffixes:
				if suffix['rule'] == 'listRange':
					nval = []
					for elem in suffix['ranges']:
						if elem['rule'] == 'intRange':
							nval += value[elem['start']['value']:elem['end']['value']+1]
						elif elem['rule'] == 'tokInteger':
							nval.append(value[elem['value']])
						else:
							print 'Unknown rule in range:', elem['rule']
							pprint(elem)
							return False
					value = nval
					if len(suffix['ranges']) == 1 and suffix['ranges'][0]['rule'] == 'tokInteger':
						value = value[0]
				elif suffix['rule'] == 'bitRange':
					nval = 0
					for elem in suffix['ranges']:
						if elem['rule'] == 'intRange':
							for i in xrange(elem['start']['value'], elem['end']['value']-1, -1):
								nval = (nval << 1) | ((value >> i) & 1)
						elif elem['rule'] == 'tokInteger':
							nval = (nval << 1) | ((value >> elem['value']) & 1)
						else:
							print 'Unknown rule in range:', elem['rule']
							pprint(elem)
							return False
					value = nval
				elif suffix['rule'] == 'attrAccess':
					if isinstance(value, tuple) and value[0] == 'defref':
						value = self.defs.named(value[1])
					value = value[1][1][suffix['attr']][1]
				else:
					print 'Unknown rule in suffix:', suffix['rule']
					pprint(suffix)
					assert False
			return value
		else:
			print 'Unknown element in expr:', value['rule']
			pprint(value)
			assert False

	def evalbang(self, op, args):
		if op == '!subst':
			find, replace, input = args
			if isinstance(input, unicode):
				return input.replace(find, replace)
			elif isinstance(input, tuple) and input[0] == 'defref':
				return replace if input == find else input
			else:
				print 'Unknown input to subst:'
				pprint(args)
		elif op == '!strconcat':
			return u''.join(args)
		elif op == '!listconcat':
			return list(itertools.chain.from_iterable(args))
		elif op == '!if':
			cmp, else_, if_ = args
			return if_ if cmp != 0 else else_
		elif op == '!eq':
			a, b = args
			return 1 if a == b else 0
		elif op == '!head':
			return args[0][0]
		elif op == '!tail':
			return args[0][1:]
		elif op == '!empty':
			return 1 if len(args[0]) == 0 else 0
		elif op == '!shl':
			a, b = args
			return a << b
		elif op == '!sra':
			a, b = args
			return a >> b
		elif op == '!srl':
			a, b = args
			return a >> b if val >= 0 else (a + 0x100000000) >> b
		elif op == '!add':
			a, b = args
			return a + b
		elif op == '!and':
			a, b = args
			return a & b
		else:
			print 'Unknown bang op:', op
			pprint(args)
			assert False

	def pushcontext(self):
		prev = self.context
		self.contexts.append(self.context)
		self.context = {}
		self.context.update(prev)

	def popcontext(self):
		self.context = self.contexts.pop()

	def pushlet(self):
		prev = self.let
		self.lets.append(self.let)
		self.let = {}
		self.let.update(prev)

	def poplet(self):
		self.let = self.lets.pop()

def interpret(filename, _includePaths=None):
	ast = parse(filename, _includePaths=None)
	return Interpreter(ast).defs

if __name__=='__main__':
	import sys
	interpret(sys.argv[1])
