from setuptools import setup


def readme():
    with open('README.md') as _file:
        return _file.read()

install_requires = [
    'colorama',
    'networkx>=0.11',
    'pytimeparse',
]
tests_require = [
    'pytest'
] + install_requires


setup(
    name='atomic',
    version='0.0.1',
    long_description=readme(),
    description='The pursuit of progress',
    author='jad-b',
    author_email='j.american.db@gmail.com',
    url='https://github.com/jad-b/atomic',
    packages=['atomic'],
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    entry_points={
        'console_scripts': [
            'atomic=atomic.cli:main',
        ]
    },
    zip_safe=False,
    include_package_data=True,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5'
    ),
)
