import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="synergyvue",
    version="0.0.3",
    author="Chad Beattie",
    author_email="chad@beattie.bz",
    description="Interface for accessing SynergyVUE data",
    long_description=long_description,
    license='MIT License',
    long_description_content_type="text/markdown",
    url="https://github.com/chadcb/synergyvue",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=['zeep>=3.4.0']
)
