# PythonXfoil

PythonXfoil is a Python module that provides an interface to run aerodynamic analyses using XFOIL. It allows users to define airfoil geometries, set analysis parameters, and execute XFOIL simulations programmatically.
Its focus is to provide an intuitive and easy-to-use alternative to similar modules.

**This project is still a WIP (Work-In-Progress)**

## Features

- Define airfoil geometries using custom coordinates.
- Set analysis parameters such as Reynolds number, Mach number, and angle of attack.
- Run XFOIL simulations in batch mode.
- Parse and retrieve aerodynamic coefficients from XFOIL output.

## Prerequisites

- Python 3.x
- XFOIL executable (`xfoil.exe` for Windows or `xfoil` for Unix-based systems) must be accessible in your system's PATH or in the same directory as the script.

## Installation

Clone the repository and navigate to the project directory:

```sh
git clone https://github.com/cc-aero/pythonxfoil.git
cd pythonxfoil
```

## Usage

### Example Script

The following example demonstrates how to use the PythonXfoil module to load airfoil coordinates, set analysis parameters, and run an XFOIL analysis.

```python
# example.py

from pythonxfoil import Airfoil
from pythonxfoil import Utils

# Load airfoil coordinates from a .dat file
with open("example-airfoils/naca2412.dat") as airfoil_file:
    airfoil_data = airfoil_file.read()

# Parse the coordinates
coords = Utils.parse_coords(airfoil_data)

# Create an Airfoil object
airfoil = Airfoil(name="NACA 2412", coords=coords)

# Set analysis parameters
airfoil.set_analysis_params(
    Re=50000,
    alpha_start=0,
    M=0.0  # Incompressible flow
)

# Run the XFOIL analysis
results = airfoil.run_analysis()

# Print the results
print(results)
```

### Module Overview

#### `pythonxfoil.py`

This module contains the `Airfoil` class and utility functions for running XFOIL analyses.

#### `Airfoil` Class

- **Initialization**: Create an airfoil object with a name and coordinates.
- **Set Analysis Parameters**: Define Reynolds number, Mach number, and angle of attack range.
- **Run Analysis**: Execute the XFOIL analysis and retrieve results.

#### `Utils` Class

- **parse_coords**: Converts multiline text of coordinates into a list of (x, y) tuples.

## Example Airfoil Data

An example airfoil data file (`naca2412.dat`) is provided in the `example-airfoils` directory.

```plaintext
NACA 2412
1.0000     0.0013
0.9500     0.0114
...
1.0000    -0.0013
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Author

@cc-aero

For any questions or issues, please open an issue on the GitHub repository.