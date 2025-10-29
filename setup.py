from setuptools import setup, find_packages

from setuptools import setup, find_packages

setup(
    name="functional_testing_tutorial",
    version="0.1.0",
    description="Tutorial package for functional testing in scientific code",
    author="Adrianna Foster",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "pandas",
        "pyyaml",
        "matplotlib",
        "seaborn",
    ],
    extras_require={
        "dev": ["pytest", "black"],
        "notebooks": ["notebook", "jupyterlab", "jupyter"]
    },
    include_package_data=True,
)