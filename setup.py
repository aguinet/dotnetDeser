from setuptools import setup

setup(name = 'dotnetDeser',
    version = '0.1.0',
    description = '.Net binary deserialization module',
    packages=['dotnetDeser'],
    author = 'Adrien Guinet',
    author_email = 'adrien@guinet.me',
    long_description = '''
''',
    classifiers=[
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Developers',
	'Topic :: Software Development :: Build Tools',
	'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.6',
	'Programming Language :: Python :: 3.7'
    ],
    install_requires=["construct"],
    keywords='deserialization .net',
    url = "https://github.com/aguinet/dotnetDeser",
    python_requires='>=3.6'
)
