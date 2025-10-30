from setuptools import setup, find_packages

setup(
    name="shirin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib",
        "seaborn",
        "numpy",
        "pandas"
    ],
<<<<<<< HEAD
    python_requires=">=3.9",  # or whatever minimum version you need
=======
>>>>>>> 98ad25ae4d7a1a08b7157f971eac37aba8804a6e
    author="Shirin",
    description="Custom visualization tools for data science projects",
)