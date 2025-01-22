"""
Author: @cc-aero
This script demonstrates the usage of the pythonxfoil module to:
      1. Load airfoil coordinates from a .dat file (NACA 2412 in this example).
      2. Parse the coordinates using Utils.parse_coords.
      3. Create an Airfoil object with the parsed data.
      4. Set analysis parameters (Re, Mach, alpha range).
      5. Run an XFOIL analysis and print the resulting aerodynamic coefficients.

Usage:
    python example_naca2412.py

Prerequisites:
    - pythonxfoil must be installed or accessible in your Python environment.
    - An example-airfoils/naca2412.dat file containing valid airfoil coordinates.
"""


from pythonxfoil import Airfoil
from pythonxfoil import Utils



airfoil_file = open("example-airfoils/naca2412.dat")
airfoil_file = airfoil_file.read()
coords = Utils.parse_coords(airfoil_file)

airfoil = Airfoil(name="airfoil",coords=coords)

airfoil.set_analysis_params(
    Re=50000,
    alpha_start=0,
    M = 0.0 # Incompressible flow
)

results = airfoil.run_analysis()

print(results)