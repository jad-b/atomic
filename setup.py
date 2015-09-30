import subprocess
import os
from setuptools import setup, find_packages


def readme():
    with open('README.md') as _file:
        return _file.read()


def requirements(reqs_file):
    if os.path.isfile(reqs_file):
        with open(reqs_file) as reqs:
            return [line.strip() for line in reqs
                    if line and not line.startswith('#')]

def latest_git_tag():
    try:
        tag = subprocess.check_output(
            ['git', 'describe', '--abbrev=0', '--tags']
        ).decode().rstrip()
    except subprocess.CalledProcessError:
        return '0.0.0'
    return tag


setup(
    name='treet',
    # Version is the most-recent git tag that's accessible via current commit.
    version=latest_git_tag(),
    long_description=readme(),
    description='Playing with tres.',
    author='jad-b',
    author_email='j.american.db@gmail.com',
    url='https://github.com/jad-b/treet',
    packages=['treet'],
    install_requires=requirements('reqs.txt'),
    entry_points={
        'console_scripts': [
            'treet=main:main',
        ]
    },
    zip_safe=False,
    include_package_data=True,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ),
)
