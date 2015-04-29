from interpreter import interpret, Dag, TableGenBits

import sys
from pprint import pprint
data = interpret(sys.argv[1])
if len(sys.argv) > 2:
	data = data.deriving(sys.argv[2])

def drepr(type, val):
	if isinstance(type, TableGenBits):
		return '{ %s }' % (', '.join(str((val >> (type.width - i - 1)) & 1) for i in xrange(type.width)))
	elif isinstance(val, tuple) and val[0] == 'defref':
		return val[1]
	elif isinstance(val, unicode):
		return '"%s"' % val.encode('unicode_escape').replace('"', '\\"')
	elif isinstance(val, list):
		return '[%s]' % (', '.join(map(lambda x: drepr(type, x), val)))
	elif isinstance(val, Dag):
		return '(%s)' % ' '.join('%s:%s' % (drepr(type, value), name) if name is not None else drepr(type, value) for name, value in val.elements)
	else:
		return `val`

for name, body in sorted(data, key=lambda a: a[0]):
	print 'def %s { // %s' % (name, ' '.join(body[0]))
	for ename, (etype, eval) in body[1].items():
		print '  %s %s = %s;' % (etype, ename, drepr(etype, eval))
	print '}'
	print
