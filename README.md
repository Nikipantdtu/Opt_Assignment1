# Assignment 1

## Overview

This repository provides the code for **Group Assignment 1** in the course **46750 - Optimization in Modern Power Systems**. It includes:

- `Task_1a.ipynb`: Notebook for Task 1a 
- `Task_1b.ipynb`: Notebook for Task 1b
- `Task_1c.ipynb`: Notebook for Task 1c
- `Task_2b.ipynb`: Notebook for Task 2b
- `data/`: Folder with data for different tasks
- `utils/`: Folder with scripts for classes, data, helper and plot functions
- Licensing information
- Dependency files (`requirements.txt`)
- A `.gitignore` file
- This `README.md` with setup and usage instructions

---

## Notebook Overview

The repository includes four Jupyter notebooks that demonstrate and visualize the optimization tasks interactively.  
These notebooks provide a step-by-step exploration of model formulations, results, and sensitivity analyses.

| Notebook | Description | Key Focus |
|-----------|--------------|-----------|
| **`Task_1a.ipynb`** | Introduces the **consumer-level flexibility model** for a single flexible load with rooftop PV generation. The model optimizes hourly load scheduling to minimize daily electricity cost under full flexibility. | Baseline optimization, PV self-consumption, cost minimization |
| **`Task_1b.ipynb`** | Extends Task 1a by including **discomfort minimization** from deviating from a preferred load profile. The consumer balances energy cost savings and comfort penalties. | Load shifting, discomfort cost, flexibility–comfort trade-off |
| **`Task_1c.ipynb`** | Adds a **battery energy storage system (BESS)** to the consumer model, combining load shifting, PV self-consumption, and storage dispatch to maximize flexibility benefits. | Battery integration, energy arbitrage, combined flexibility modeling |
| **`Task_2b.ipynb`** | Expands from operational optimization to **battery investment analysis**. Evaluates optimal battery sizing, profitability, and payback under different market scenarios. | Investment optimization, NPV analysis, sensitivity to price scenarios |

---

## Installation

Follow these steps to set up your environment and install dependencies.

### 1. **Clone the repository**

Create a copy of this repository for your group.

### 2. **Create a virtual environment**

Set up a clean Python environment and install required packages.

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# On Windows cmd: venv\Scripts\activate.bat
# On Windows PowerShell: venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Getting Started

1. **Install dependencies** as described above.
2. **Explore the solved scripts** for each task:
    - `Task_1a.py`
    - `Task_1b.py`
    - `Task_1c.py`
    - `Task_2b.py`

## Input Data Structure

Base datasets are located under the `data/question_name` directories:

- **Consumers Data (`consumers.json`)**  
    - `consumer_id`, `connection_bus`, `list_appliances`
- **Appliances Data (`appliance_params.json`)**  
    - DERs: `DER_id`, `DER_type`, `max_power_kW`, etc.
    - Loads: `load_id`, `load_type`, `max_load_kWh_per_hour`, etc.
    - Storages: `storage_id`, `storage_capacity_kWh`, etc.
- **Usage Preferences (`usage_preference.json`)**  
    - `consumer_id`, grid/DER/load/storage/heat pump preferences
- **DER Production (`DER_production.json`)**  
    - `consumer_id`, `DER_type`, `hourly_profile_ratio`
- **Bus Data (`bus_params.json`)**  
    - `bus_id`, `import_tariff`, `export_tariff`, `max_import_kw`, etc.



