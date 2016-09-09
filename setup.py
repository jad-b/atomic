from setuptools import setup


def readme():
    with open('README.md') as _file:
        return _file.read()

setup(
    name='atomic',
    version='0.0.1',
    long_description=readme(),
    description='The pursuit of progress',
    author='jad-b',
    author_email='j.american.db@gmail.com',
    url='https://github.com/jad-b/atomic',
    packages=['atomic'],
    install_requires=(
        'networkx>=0.11',
        'pytimeparse',
        'pytest'
    ),
    entry_points={
        'console_scripts': [
            'valence=atomic.shell:main',
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
