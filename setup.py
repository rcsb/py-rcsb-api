# File: setup.py
# Date: 20-May-2024
#
# Update:
#
import re

from setuptools import find_packages
from setuptools import setup

packages = []
thisPackage = "rcsb-api"

with open("rcsbapi/__init__.py", "r", encoding="utf-8") as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)

# Load packages from requirements*.txt
with open("requirements.txt", "r", encoding="utf-8") as ifh:
    packagesRequired = [ln.strip() for ln in ifh.readlines()]

with open("README.md", "r", encoding="utf-8") as ifh:
    longDescription = ifh.read()

if not version:
    raise RuntimeError("Cannot find version information")

setup(
    name=thisPackage,
    version=version,
    description="Python package interface for RCSB.org API services",
    long_description_content_type="text/markdown",
    long_description=longDescription,
    python_requires=">=3.8,<4.0",
    author="Dennis Piehl",
    author_email="dennis.piehl@rcsb.org",
    url="https://github.com/rcsb/py-rcsb-api",
    #
    license="MIT",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Development Status :: 4 - Beta",
        # 'Development Status :: 5 - Production/Stable',
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Typing :: Typed",
    ],
    entry_points={"console_scripts": []},
    #
    install_requires=packagesRequired,
    packages=find_packages(exclude=["tests", "tests-*", "tests.*"]),
    package_data={
        # If any package contains *.md or *.rst ...  files, include them:
        "": ["*.md", "*.rst", "*.txt", "*.cfg", "rcsbapi/*/resources/*"]
    },
    #
    test_suite="tests",
    tests_require=["tox"],
    #
    # Not configured ...
    extras_require={
        "dev": ["check-manifest"],
        "test": ["coverage"],
        "tests": ["tox", "pylint", "black>=21.5b1", "flake8"],
        # should match docs/requirements.txt
        "docs": ["sphinx", "sphinx-rtd-theme", "myst-parser"],
    },
    # Added for
    command_options={"build_sphinx": {"project": ("setup.py", thisPackage), "version": ("setup.py", version), "release": ("setup.py", version)}},
    # This setting for namespace package support -
    zip_safe=False,
)
