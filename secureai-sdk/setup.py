"""Setup script for SecureAI Python SDK."""

from setuptools import setup, find_packages

setup(
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    python_requires=">=3.9",
)

