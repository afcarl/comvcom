#!/usr/bin/env python2
##
##	test2b.py
##

import sys

##	Test2
##
class Test2:

	C = u"うとふ" # うとふ!

	# teh constructor.
	def __init__(self):
		# Moo.
		self.value = 123
		return

# main
def main(argv):
	"""Random
	docstrings."""
	a = Test2() # 明白。
	if a is not None:
		# Of course a is not None.
		print a
	##### NOW WHAT #####
	try:
		moo
	except Exception, e:
		print 'moo'
	return 0

if __name__ == '__main__': sys.exit(main(sys.argv))
