[![DOI](https://zenodo.org/badge/1271071226.svg)](https://doi.org/10.5281/zenodo.20777137)
[![License](https://img.shields.io/badge/License-CECILL%202.1-green)](/LICENSE-EN.txt)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](/CODE_OF_CONDUCT.md)
[![Unit tests](https://github.com/AntoineTeixeira/matmat-ademe/actions/workflows/ci.yml/badge.svg)](https://github.com/AntoineTeixeira/matmat-ademe/actions/workflows/ci.yml)

# MatMat model

## Presentation

> **Beta pre-release (v0.9.1-beta)**
> 
> This repository contains the first public open-source release of MatMat. Some
> internal development utilities, legacy data conversion scripts, and experimental
> modules are intentionally excluded from this release. The public API,
> documentation, and package structure may evolve before the stable v1.0.0 release.

MatMat is released as an open-source beta version to support transparency,
reproducibility, review, and reuse of the research and assessment activities
for which it has been developed and applied. The first version of MatMat software
was developed during Antoine Teixeira's PhD research conducted at ADEME and CIRED,
with the support of CGDD and SMASH. The framework was subsequently refactored 
from scratch, consolidated, and extended through software engineering 
developments performed by ADEME in collaboration with Julien Grand. MatMat is 
now used in several research and assessment projects conducted by ADEME and its
research partners, including CIRED, DGEC, Inria, Insee, RTE, SDES and SMASH.

This beta release is archived for citation and review purposes. A consolidated
stable release (v1.0.0) is planned following additional documentation,
validation, and software improvements.

MatMat (Material Matrices) is a modular open-source Python framework for 
Environmentally-Extended Input-Output (EEIO) modelling and prospective 
environmental and socio-economic impact assessment.

The framework is designed to assess the environmental pressures and socio-economic
implications of global, regional and country-driven transition pathways along 
global supply chains. It enables the consistent evaluation of current and future
sustainability challenges associated with global, regional and national climate,
energy, industrial, and resource strategies.

To support comprehensive global, regional and national-scale assessments,
MatMat supports both closed-economy assessments at the global scale and
open-economy assessments at national and regional scales through a
Single-country National Accounts Consistent (SNAC) footprint approach,
combining a detailed representation of the domestic economy with a
multi-regional description of international trade. This allows the simultaneous
assessment of production-based and consumption-based indicators and their 
associated environmental and socio-economic impacts.

A key methodological feature of MatMat is its ability to analyse the 
interdependencies between greenhouse gas emissions, capital accumulation, 
material production, and final consumption along global supply chains. Through 
the integration of capital flow matrices, the framework enables the 
endogenisation of capital formation in consumption-based environmental analyses
and supports the investigation of long-term transition pathways.

MatMat also provides analytical tools for investigating the contribution of 
sectors and supply chains to national environmental pressures and supports the 
translation of qualitative policy narratives and expert assumptions into 
coherent economy-wide prospective scenarios.

Beyond its methodological capabilities, MatMat places strong emphasis on software
engineering principles. Developed in Python using object-oriented design principles,
the framework prioritises transparency, modularity, reusability, extensibility,
and reproducibility, addressing key limitations of many existing EEIO tools for
long-term policy-oriented analysis.

MatMat was primarily developed by Antoine Teixeira and Julien Grand at ADEME.


## Related publications and materials

The publications and resources below illustrate the progressive development
of MatMat, from its methodological foundations and calibration databases to
its applications in scientific research and public policy assessment.

### Earlier methodological materials

The following materials document earlier stages of the MatMat methodological
development. They provide useful background on the modelling approach and selected
applications, but they may not fully reflect the current software architecture,
package structure, API, and implementation choices of the v0.9.1-beta release.

- Teixeira A., Grand J. & al. (2025). *MatMat – A modular Input-Output
  framework: Assessing country-driven environmental and socio-economic impacts 
  of forward-looking scenarios along global supply chains.* Conference 
  presentation. https://hal.science/hal-05076595v1/file/250ra.pdf
- Teixeira A. (2024). *MatMat-Hybrid Input-Output framework to estimate 
  country-level carbon and material footprints in future scenarios*. Working
  paper. https://hal.science/hal-04672116/
- Teixeira A. & al. (2020). *Construction de matrices de flux de matières pour 
  une prospective intégrée énergie-matières-économie.* Report. 
  https://hal.science/hal-03128599/

### Related databases and calibration resources

MatMat relies on dedicated calibration databases and prospective datasets
developed to construct French environmentally-extended input-output models
and future transition scenarios.

Some datasets contain third-party proprietary information and are therefore
archived under restricted access. Their metadata and documentation remain
publicly available for transparency and reproducibility purposes.

- Chaigneau Y., Teixeira A. & Vicard F. (2026). *Scenario-based consumption-
  based GHG emissions for the French National Low-Carbon Strategy (SNBC-3),
  2019–2050.* Zenodo (restricted access).
- Teixeira A. & Vicard F. (2026). *Scenario-based consumption-based GHG 
  emissions and material extraction results for ADEME Transition(s) 2050 
  pathways in France (2015–2050) using the MatMat EEIO model.* Zenodo. 
  https://doi.org/10.5281/zenodo.18418964
- Teixeira A. & Fontaine B. (2026). *Hybrid Input-Output calibration database 
  for the French MatMat model: SNAC-S-based GHG emissions and raw material 
  consumption-based assessment (2015–2019).* Zenodo (restricted access). 
  https://doi.org/10.5281/zenodo.10658659

### Policy applications

MatMat has contributed to the assessment and development of the French
National Low-Carbon Strategy (SNBC-3) and ADEME's Transition(s) 2050
scenarios. Furthermore, MatMat and its associated methodological developments
have contributed to ongoing discussions on the estimation of the French carbon 
footprint and the development of official footprint accounting methodologies 
by public institutions, including SDES and INSEE.

- Larrieu S., Baude M. & Teixeira A. (2026). *Estimating the French carbon
  footprint from 1990 to 2024 - An official statistics methodology based on FIGARO.*
  https://hal.science/hal-05620182v1
- French Ministry for Ecological Transition (2025). *French National Low Carbon
  Strategy (SNBC-3).*
  https://www.ecologie.gouv.fr/sites/default/files/documents/2025-%20Projet%20SNBC%203%20compress-Partie%201_Vfin_vdef_clean_clean%20COMPRESS.pdf
- Vicard F. & Teixeira A. (2024). *Prospective - Transition(s) 2050 - Feuilleton
  Empreintes : Évaluation des empreintes carbone et matières des scénarios 
  Transition(s) 2050.*
  https://librairie.ademe.fr/changement-climatique/6250-prospective-transitions-2050-feuilleton-empreintes.html

### Research applications

- Teixeira A. & Vicard F. (2026). Reducing GHG emissions and raw materials
  embodied in imports: Assessing a cross-sectoral sufficiency-oriented national
  climate strategy in France. Journal of Industrial Ecology.
  https://doi.org/10.1007/s44498-026-00016-0
- Fontaine B., Lefèvre J., Teixeira A. & Vicard F. (2026). Sufficiency as
  a key driver of domestic and imported emissions reductions in France’s 
  Net-Zero Transition. Environmental Research Letters. 
  https://doi.org/10.1088/1748-9326/ae7e98
- Teixeira A. & Lefèvre J. (2025). Global supply chains and domestic climate
  policy: Addressing the substantial material-related carbon footprint of final
  consumption in France. Journal of Industrial Ecology.
  https://doi.org/10.1111/jiec.70001


## Use MatMat as a Python library

### Installation instructions
If you want to use MatMat as a python library, here are the instructions, depending on your operating system.
Note that MatMat is currently functional and tested under **Python3.11**

---

### Manual procedure
<details>
<summary>Linux environment</summary>
  
### 1. Install Python 3.11
```commandline
sudo apt install python3.11
```
### 2. Install venv
```commandline
sudo apt-get install python3.11-venv
```
### 3. Create your virtual environment
```commandline
python3.11 -m venv env
```
### 4. Activate your virtual environment
```commandline
source env/bin/activate
```
### 5. (optional) Update pip
```commandline
python -m pip install --upgrade pip
```
### 6. Install MatMat
```commandline
# Replace <version> by the MatMat version you want to work with
python -m pip install "matmat @ git+https://github.com/AntoineTeixeira/matmat-ademe.git@<version>"
```
</details>

<details>
<summary>Windows environment</summary>

### 1. Install **Python3.11**
from [python.org](https://www.python.org/downloads/) 
(check "Add Python to PATH" during installation)
### 2. Create your virtual environment
```commandline
py -3.11 -m venv env
```
### 3. Activate your virtual environment
```commandline
env\Scripts\activate
```
### 4. (optional) Update pip
```commandline
python -m pip install --upgrade pip
```
### 5. Install MatMat
```commandline
# Replace <version> by the MatMat version you want to work with
python -m pip install "matmat @ git+https://github.com/AntoineTeixeira/matmat-ademe.git@<version>"
```
</details>

<details>
<summary>MacOS environment</summary>

### 1. Install Python 3.11
- From python.org: https://www.python.org/downloads/  
- Or via Homebrew:
```bash
brew install python@3.11
```
### 2. Verify Python 3.11 is available
After installation, check that Python 3.11 is accessible:
```bash
python3.11 --version
```

If the command is not found:
- Try:
  ```bash
  python3 --version
  ```
- If this shows **Python 3.11.x**, you can use `python3` instead of `python3.11`
- Otherwise, ensure Python 3.11 is correctly installed and available in your PATH
### 3. Create your virtual environment

Using Python 3.11:

```bash
python3.11 -m venv env
```

(Or `python3 -m venv env` if it points to Python 3.11)
### 4. Activate your virtual environment

```bash
source env/bin/activate
```
### 5. (optional) Update pip
```commandline
python -m pip install --upgrade pip
```
### 6. Install MatMat

```bash
# Replace <version> by the MatMat version you want to work with
python -m pip install "matmat @ git+https://github.com/AntoineTeixeira/matmat-ademe.git@<version>"
```

</details>

---

### Initialization of MatMat

Once you have installed the MatMat package, you need to initialize your MatMat workspace.

First, execute the *init* command:
``python -m matmat.cli --init``

This will generate:
- the configuration file **config.toml**: it permits to manage MatMat global configuration
- the settings JSON files: they permit to configure MatMat workflows

**NOTE:** if you re-run the command *init*:
- if the config.toml file already exists, it will not be overwritten
- if a settings file already exists, MatMat will ask for confirmation before overwriting it

#### File config.toml
You need to configure the two parameters **data_dir** and **settings_dir**

- **data_dir:** it defines the absolute path to your data directory. 
</br>By default it points towards the local data folder (relatively to the directory where
you executed the **init** command)
</br>You may want to update it if you prefer to manage your data somewhere else.
- **settings_dir:** it defines the absolute path to the settings directory. 
</br>The *init* command has generated a settings directory containing the settings JSON files.
</br>You may want to update it if you prefer to move the settings directory somewhere else.

**NOTE:** For all OS, prefer using '/' only in path definition. MatMat will handle it.

#### Folder settings
The settings folder has been generated in your working directory.
If you move it, you need to update the **config.toml** file accordingly.

In this folder, there is one sub-folder for each workflow type:
- adapter
- pipeline
- engine
- analyses

In each of these folders, there is one JSON settings file for each workflow.
To configure a workflow execution, you need to update the corresponding settings
file.

When you run a workflow from the command line, MatMat will automatically read
the associated settings JSON file.
</br>The convention for the location of settings JSON file is: **settings/<workflow_type>s/<workflow_name>_settings.json**

**Example:** the file **settings/adapters/exiobase3_eeio_settings.json** shall be updated before
running the adapter exiobase3_eeio.

### How to run workflows
MatMat offers a Command Line Interface (CLI).
For details about how to use it, use the integrated help by running the command:

``python -m matmat.cli -h``

The generic command to run a workflow is:

``python -m matmat.cli -<type> <name>``

| Workflow | Type | Name(s)                                           |
|----------|---|---------------------------------------------------|
| adapter  | a | exiobase3_eeio<br/>manual                         |
| pipeline | p | gmrio_to_snac_s<br/>aggregation<br/>union         |
| engine | e | eeio                                              |
| analysis | an | *no analysis workflows available in this version* |

**Examples:**

``python -m matmat.cli -a exiobase3_eeio``

``python -m matmat.cli -p gmrio_to_snac_s``

``python -m matmat.cli -e eeio``

### Usage examples
Examples and tutorials are currently under development and will be progressively
added before the v1.0.0 release.

## Contribute to MatMat project
This section is dedicated to contributors.
Before contributing to the project, please read the [contribution](/CONTRIBUTING.md) rules and the [code of conduct](/CODE_OF_CONDUCT.md).
Thank you.

### Installation instructions

- **Python** == 3.11

- Install **Python3.11**
```commandline
sudo apt install python3.11
```
- Retrieve source code
```commandline
mkdir <your_work_directory>
cd <your_work_directory>
git clone https://github.com/AntoineTeixeira/matmat-ademe.git
```
- Switch to a new branch to start modifications
```commandline
git checkout -b <branch_name>
```
- Configure your virtual environment (in your work directory)
```commandline
sudo apt-get install python3.11-venv
python3.11 -m venv env
source env/bin/activate
```
- Install matmat dependencies

```commandline
# For mandatory dependencies
pip install .

# For mandatory dependencies + test framework
pip install .[dev]

# For mandatory dependencies + documentation
pip install .[docs]

# For all dependencies
pip install .[dev,docs]
```

### Tests
Unit and integration tests are done with **Pytest**.

To execute the unit tests, you need to have set up your virtual environment as described earlier.
It shall be named **env** for the script to work. Otherwise, you need to execute them manually
or to update the script.

Once the virtual environment **env** is set up, just go to the **tests** directory and execute:
- If necessary, give the execution permission to run_tests.sh
```commandline
chmod +x run_tests.sh
```
- Perform unit tests in developer mode
  (in this configuration, each dataframe is randomized globally, which means its cells have the same value,
  which means less execution time. Moreover, the execution stops at the first failed test)
```commandline
./run_tests.sh dev
```
- Perform official unit tests campaign
  (in this configuration, each dataframe cell is randomized individually, which takes more execution time)
```commandline
./run_tests.sh full
```


To perform tests individually or as a group, use **pytest** command line.

#### Examples
- To run all tests related to MatMat core package
```commandline
pytest unit_tests/core
```
- To run all tests related to system calcul strategy
```commandline
pytest unit_tests/core/accounts/system/strategies/calcul
```

### Documentation
The documentation is generated automatically with **Sphinx**, directly from docstrings written
in the code. All docstrings must follow the template defined in the [docstring template](/docs/DOCSTRING_TEMPLATE.py).

The folder **docs/source** defines the configuration of **Sphinx** tool as well as the
.rst files (reStructuredText) which define the documentation architecture.

- To generate the documentation in HTML format, 
go to the directory **docs** and execute the following command:
```commandline
make html
```
The documentation will be generated in **docs/build/html**.
Access it by opening **index.html** with your favorite browser.

- To generate in PDF format, you need to install a few packages first:
```commandline
sudo apt-get install latexmk
sudo apt-get install texlive-full
```
The installation may take a while... once it is finished, go to the directory
**docs** and execute the following command:
```
make latexpdf
```
The documentation will be generated in **docs/build/latex**.
The PDF file is **matmat.pdf**.


## License

MatMat is available under the license "CeCILL version 2.1" as defined in files [LICENSE-EN.txt](/LICENSE-EN.txt) and [LICENSE-FR.txt](LICENSE-FR.txt).

For more information, you can visit [CeCILL website](https://cecill.info/index.en.html).


## Citation

If you use MatMat in academic research, please cite the software release
associated with your work.

Citation metadata are provided in the `CITATION.cff` file.


## Contact information

| Name | Role | Contact |
| ---- | ---- | ------- |
| Antoine Teixeira | Scientific lead, methodological design, development | antoine.teixeira@ademe.fr |
| Julien Grand | Software engineering, refactoring, and development | jgrand.pro@proton.me |


## Release history

| Version    | Date       | Description                                                                                   |
| ---------- | ---------- | --------------------------------------------------------------------------------------------- |
| 0.9.1-beta | 2026-07-05 | Maintenance beta release restoring missing package data and updating GitHub Actions workflows |
| 0.9.0-beta | 2026-06-20 | First public open-source beta release                                                         |
