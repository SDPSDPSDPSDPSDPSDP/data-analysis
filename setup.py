from setuptools import setup, find_packages

setup(
    name="shirin",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "seaborn"
    ],
    python_requires=">=3.9",
    author="Shirin",
    description="Custom visualization tools for data science projects",
)