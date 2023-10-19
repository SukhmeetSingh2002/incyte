from setuptools import setup

# Read the contents of README.md
with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="incyte",
    version="1.0.0",
    packages=["incyte"],
    entry_points={
        "console_scripts": [
            "incyte = incyte.compare:main",
        ],
    },
    install_requires=[
        "rich",
    ],
    python_requires=">=3.6",
    description="A stress testing tool for comparing the output of two programs",
    long_description=long_description,
    long_description_content_type="text/markdown",  
    license="MIT",
    keywords="compare, output, diff, stress testing, testing, software testing, stress tests, stress test tool",
)
