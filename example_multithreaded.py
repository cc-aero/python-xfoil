# example_multithreaded.py

from pythonxfoil import Airfoil
from pythonxfoil import Utils

# Load airfoil coordinates from a .dat file
with open("example-airfoils/naca2412.dat") as airfoil_file:
    airfoil_data = airfoil_file.read()

# Parse the coordinates
coords = Utils.parse_coords(airfoil_data)

# Create an Airfoil object
airfoil = Airfoil(name="NACA 2412", coords=coords)

# Set analysis parameters with lists of values
Re_list = [30000, 100000, 120000]
alpha_start_list = [1, 1, 1]
M_list = [0.5, 0.3, 0.1]

airfoil.set_analysis_params(
    Re=Re_list,
    alpha_start=alpha_start_list,
    M=M_list,
)

# Run the multithreaded XFOIL analysis
results = airfoil.run_multithreaded_analysis()

# Print the results
for result in results:
    print(result)