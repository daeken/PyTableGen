from parser import parse
from pprint import pprint

class Interpreter(object):
	def __init__(self, ast):
		self.ast = ast

		self.classes = {}
		self.multiclasses = {}

		self.contexts = []
		self.context = None
		self.cur_def = []
		self.defs = []

		self.define(ast)
		self.execute(ast)

	def define(self, elem):
		if isinstance(elem, dict):
			assert 'rule' in elem
			if elem['rule'] == 'tclass':
				self.classes[elem['name']] = dict(
					name=elem['name'],
					baseClasses=elem['baseClasses'] if elem['baseClasses'] is not None else [],  
					args=elem['args'] if elem['args'] is not None else [], 
					body=elem['body'] if elem['body'] != ';' else []
				)
			elif elem['rule'] not in ('tdef', ):
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
				self.cur_def = [[], ('NAME', 'string', elem['name'])]
				self.context['NAME'] = elem['name']
				self.defs.append((elem['name'], self.cur_def))
				for cls in elem['baseClasses']:
					self.evalclass(cls['id'], cls['args'])
				if elem['body'] != ';':
					self.evalbody(elem['body'])
				self.popcontext()
			elif elem['rule'] not in ('tclass', ):
				print 'Unhandled rule:', elem['rule']
				assert False
		elif isinstance(elem, list):
			return map(self.execute, elem)
		else:
			print 'Unknown element:', 
			pprint(elem)
			assert False

	def evalclass(self, name, args):
		cls = self.classes[name]
		assert len(args) == len(cls['args'])
		for i, elem in enumerate(cls['args']):
			self.context[elem['name']] = self.evalexpr(args[i])

		for base in cls['baseClasses']:
			self.evalclass(base['id'], base['args'])

		self.cur_def[0].append(name)
		
		self.evalbody(self.classes[name]['body'])

	def evalbody(self, body):
		for elem in body:
			if elem['rule'] == 'declaration':
				val = self.evalexpr(elem['value'])
				self.cur_def.append((elem['name'], elem['type'], val))
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
		else:
			print 'Unknown bang op:', op
			pprint(args)
			assert False

	def pushcontext(self):
		self.contexts.append(self.context)
		self.context = {}

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
