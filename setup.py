import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()



with open(os.path.join("uvm_python_rdl", "__about__.py")) as f:
    v_dict = {}
    exec(f.read(), v_dict)
    version = v_dict['__version__']

setuptools.setup(
    name="uvm-python-rdl",
    version=version,
    author="Tuomas Poikela",
    description="Generate UVM (uvm-python) register model from compiled SystemRDL input",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=['uvm_python_rdl'],
    include_package_data=True,
    install_requires=[
        "systemrdl-compiler>=1.12.0",
        "jinja2",
    ],
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ),
    project_urls={
        "Source": "",
        "Tracker": ""
    },
)
