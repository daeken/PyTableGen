from parser import parse
from pprint import pprint
from collections import OrderedDict

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
			return TableGenList(type['type'])
		else:
			print 'Unknown rule for TableGenType:', type['rule']
			pprint(type)
			assert False

class TableGenList(TableGenType):
	def __str__(self):
		return 'list<%s>' % self.type

class Interpreter(object):
	def __init__(self, ast):
		self.ast = ast

		self.classes = {}
		self.multiclasses = {}

		self.basenames = []
		self.contexts = []
		self.context = {}
		self.cur_def = None
		self.defs = []

		self.define(ast)
		self.execute(ast)

	def define(self, elem):
		if isinstance(elem, dict):
			assert 'rule' in elem
			if elem['rule'] == 'tclass':
				self.classes[elem['name']] = dict(
					name=elem['name'],
					bases=elem['bases'] if elem['bases'] is not None else [],  
					args=elem['args'] if elem['args'] is not None else [], 
					body=elem['body'] if elem['body'] != ';' else []
				)
			elif elem['rule'] == 'multiClass':
				self.multiclasses[elem['name']] = dict(
					name=elem['name'],
					bases=elem['bases'] if elem['bases'] is not None else [],  
					args=elem['args'] if elem['args'] is not None else [], 
					body=elem['body'] if elem['body'] != ';' else []
				)
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
				NAME = u''.join(self.basenames) + elem['name']
				self.cur_def = ([], OrderedDict(NAME=('string', NAME)))
				self.context['NAME'] = NAME
				self.defs.append((NAME, self.cur_def))
				for cls in elem['bases']:
					self.evalclass(cls['id'], cls['args'])
				if elem['body'] != ';':
					self.evalbody(elem['body'])
				self.popcontext()
			elif elem['rule'] == 'defm':
				if elem['name'] is not None:
					self.basenames.append(elem['name'])
				for cls in elem['bases']:
					self.evalmulticlass(cls['id'], cls['args'])
				if elem['name'] is not None:
					self.basenames.pop()
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
		cls = self.classes[name]
		self.handleargs(cls['args'], args)

		for base in cls['bases']:
			self.evalclass(base['id'], base['args'])

		self.cur_def[0].append(name)

		self.evalbody(self.classes[name]['body'])

	def evalmulticlass(self, name, args):
		mcls = self.multiclasses[name]

		self.pushcontext()

		self.handleargs(cls['args'], args)
		self.execute(mcls['body'])

		self.popcontext()

	def evalbody(self, body):
		for elem in body:
			if elem['rule'] == 'declaration':
				val = self.evalexpr(elem['value'])
				if elem['type'] == 'let':
					assert elem['name'] in self.cur_def[1]
					type = self.cur_def[1][elem['name']][0]
					self.cur_def[1][elem['name']] = (type, val)
				else:
					self.cur_def[1][elem['name']] = (TableGenType.cast(elem['type']), val)
				self.context[elem['name']] = val
			else:
				print 'Unknown element in body:', elem['rule']
				assert False

	def evalexpr(self, value):
		if value['rule'] == 'value':
			value = value['value']
			if isinstance(value, dict):
				if value['rule'] in ('tokString', 'tokInteger'):
					return value['value']
				elif value['rule'] == 'bangValue':
					return self.evalbang(value['operator'], map(self.evalexpr, value['args']))
				elif value['rule'] == 'simpleList':
					assert value['type'] is None
					return map(self.evalexpr, value['values_']) if value['values_'] is not None else []
				else:
					print 'Unknown value in expr:', value['rule']
					pprint(value)
					assert False
			elif isinstance(value, unicode):
				if value in self.context:
					return self.context[value]
				elif value in [cdef[0] for cdef in self.defs]:
					return ('defref', value)
				else:
					print 'Unknown name:', value
					assert False
			elif isinstance(value, int):
				return value
			else:
				print 'Unknown value in expr'
				pprint(value)
				assert False
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
		elif op == '!if':
			cmp, if_, else_ = args
			return if_ if cmp != 0 else else_
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

def interpret(filename, source):
	ast = parse(filename, source)
	return Interpreter(ast)

if __name__=='__main__':
	import sys
	with open(sys.argv[1]) as f:
		text = f.read()
	interpret(sys.argv[1], text)
