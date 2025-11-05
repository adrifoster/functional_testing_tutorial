# Functional Testing Tutorial

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/adrifoster/functional_testing_tutorial/main?filepath=notebooks)

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/adrifoster/functional_testing_tutorial/blob/main/notebooks/00_Intro.html)

Welcome! This tutorial uses Python to explore **functional testing** in scientific code. The 
tutorial notebooks rely on a small library containing fire code examples (`fire_equations.py`,
`fuel_class.py`, etc.). This code is translated from the SPITFIRE module within the 
[FATES](https://github.com/NGEET/fates) repository.

## Launching notebooks

Click [here](https://mybinder.org/v2/gh/adrifoster/functional_testing_tutorial/main?filepath=notebooks) to launch a Jupyter Hub online via binder to interactively explore the notebooks.

A static Jupyter Book is also available [here](https://adrifoster.github.io/functional_testing_tutorial/00_Intro.html).

## Local Install
Follow these steps to set up your environment and install the library.

### 1. Clone the repository

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
├─ figs/
├─ parameter_files/
├─ setup.py
├─ environment.yml
└─ requirements.txt
```

### 2. Create Python environment

#### Option A: Conda (recommended)

In a terminal window type:

```
conda env create -f environment.yml
conda activate functional-testing-tutorial
```

#### Option B: Pip (if not using Conda)

In a terminal window type:

```
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
.venv\Scripts\activate          # Windows

pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install tutorial library

Once your environment is active, install the Python package in **editable mode**:

```
pip install -e .
```

This makes `functional_testing_tutorial` importable anywhere in the environment and 
allows changes to `src/` to take effect immediately.

#### Test the installation

```
python -c "from fire_model.fire_equations import FireEquations; print('Library installed!')"
```

If you see `Library installed!`, you're good to go!
