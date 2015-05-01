from distutils.core import setup

setup(name='PyTableGen',
		version='0.2', 
		description='Python port of LLVM\'s TableGen tool', 
		author='Cody Brocious', 
		author_email='cody.brocious@gmail.com', 
		packages=['tblgen'], 
		scripts=['scripts/pytblgen'], 
		install_requires=[
			'grako',
		]
	)
