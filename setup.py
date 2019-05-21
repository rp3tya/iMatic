import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iMatic",
    version="0.2",
    author="rp3tya",
    author_email="rpetya@hotmail.com",
    description="iMatic client library for 8/16 channel relay board controllers by SainSmart",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rp3tya/iMatic",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords='sainsmart imatic relay',
)

