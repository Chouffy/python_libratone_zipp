import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="python_libratone_zipp",
    packages=["python_libratone_zipp"],
    version="1.1.1",
    description="Control a Libratone Zipp speaker with a Python library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Chouffy/python_libratone_zipp",
    project_urls={
        "Bug Tracker": "https://github.com/Chouffy/python_libratone_zipp/issues",
    },
    author="Chouffy",
    author_email="git@chouffy.net",
    license="The Unlicense (Unlicense)",
    classifiers=[
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Programming Language :: Python :: 3",
    ],
)
