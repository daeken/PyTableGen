from interpreter import interpret

import sys
from pprint import pprint
with open(sys.argv[1]) as f:
	text = f.read()
data = interpret(sys.argv[1], text)

def drepr(val):
	if isinstance(val, tuple) and val[0] == 'defref':
		return val[1]
	elif isinstance(val, unicode):
		return '"%s"' % val.encode('unicode_escape').replace('"', '\\"')
	elif isinstance(val, list):
		return '[%s]' % (', '.join(map(drepr, val)))
	else:
		return `val`

for name, body in data.defs:
	print 'def %s { // %s' % (name, ' '.join(body[0]))
	for ename, (etype, eval) in body[1].items():
		print '  %s %s = %s;' % (etype, ename, drepr(eval))
	print '}'
	print
