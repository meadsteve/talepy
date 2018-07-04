import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "talepy",
    packages = [".", "talepy"],
    package_data={
        # root markdown files should be packaged
        '.': ['*.md'],
    },
    version = "0.2.0",
    description = "Distributed Transactions Helper",
    author = "Steve Brazier",
    author_email = "meadsteve@gmail.com",
    url = "https://github.com/meadsteve/talepy",
    keywords = ["saga", "distributed transaction"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        ],
    long_description = read("README.md"),
    long_description_content_type='text/markdown'
)