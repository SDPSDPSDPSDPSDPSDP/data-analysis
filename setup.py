from setuptools import setup, find_packages

setup(
    name="shirin",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "seaborn",
        "numpy",
        "pandas"
    ],
    python_requires=">=3.9",
    author="Shirin",
    description="Custom visualization tools for data science projects",
)