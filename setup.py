from setuptools import find_namespace_packages, setup

with open("README.rst") as fp:
    long_description = fp.read()
long_description = long_description \
    .replace(".. shtest::", ".. code-block::\n") \
    .replace(".. sh::", "..")

setup(
    name="sphinxcontrib-shtest",
    version="0.5.0",
    packages=find_namespace_packages(),
    install_requires=[
        "sphinx",
    ],
    long_description_content_type="text/x-rst",
    long_description=long_description,
    url="https://github.com/tillahoffmann/sphinxcontrib-shtest",
)
