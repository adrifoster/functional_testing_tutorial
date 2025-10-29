# Functional Testing Tutorial - Setup Instructions

Welcome! This tutorial uses Python to explore **functional testing** in scientific code. The 
tutorial notebooks rely on a small library containing fire code examples (`fire_equations.py`,
`fuel_class.py`, etc.). This code is translated from the SPITFIRE module within the 
[FATES](https://github.com/NGEET/fates) repository.

Follow these steps to set up your environment and install the library.

## 1. Clone the repository

Open a terminal and run:

```
git clone https://github.com/adrifoster/functional_testing_tutorial
cd functional_testing_tutorial
```

Your repository should have this structure:

```
functional_testing_tutorial/
├─ src/
│  ├─ __init__.py
│  ├─ fire_equations.py
│  ├─ fire_params.py
│  ├─ fire_weather_class.py
│  ├─ fuel_class.py
│  ├─ nesterov_fire_weather.py
│  ├─ fuel_types.py
│  └─ testing/
│     ├─ __init__.py
│     ├─ synthetic_fuel_models.py
│     └─ testing_shr.py
├─ notebooks/
├─ data/
├─ parameter_files/
├─ setup.py
├─ environment.yml
└─ requirements.txt
```

## 2. Create Python environment

### Option A: Conda (recommended)

In a terminal window type:

```
conda env create -f environment.yml
conda activate functional-testing-tutorial
```

### Option B: Pip (if not using Conda)

In a terminal window type:

```
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
.venv\Scripts\activate          # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Install tutorial library

Once your environment is active, install the Python package in **editable mode**:

```
pip install -e .
```

This makes `functional_testing_tutorial` importable anywhere in the environment and 
allows changes to `src/` to take effect immediately.

### Test the installation

```
python -c "from functional_testing_tutorial.fire_equations import FireEquations; print('Library installed!')"
```

If you see `Library installed!`, you're good to go!
