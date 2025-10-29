from setuptools import setup, find_packages

setup(
    name="fire_model",
    version="0.1.0",
    description="package for running a minimal fire model",
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