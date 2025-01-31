import math
import os
import subprocess
import tempfile
import concurrent.futures

class Airfoil:
    """
    Author: @cc-aero
    Represents a 2D airfoil for analysis.

    Users can define an airfoil by providing a custom set of (x, y) coordinates.

    Example usage:
        # Create airfoil by coords
        coords =  [(1.0, 0.0013), (0.95, 0.0114), ..., (1.0, -0.0013)]
        af1 = Airfoil(name="NACA2412", coords = coords)
        af1.set_analysis_params(Re=1e6, alpha_start=0, alpha_end=10, alpha_step=2)
        print(af1.run_analysis())
    """
    def __init__(self, name: str = None, coords: list = None):
        """
        Initialize the Airfoil object.

        :param name: String identifying out airfoil (e.g., "c150 airfoil").
                       Used to identify the airfoil in Xfoil. Irrelevant for now.
        :param coords: A list of (x, y) tuples defining the airfoil geometry.


        //!TODO: Parse a NACA string and generate coordinates
        """
        if coords is not None:
            self.name = "PythonXfoil Airfoil"
            self.coords = coords
        else:
            raise ValueError("Must provide 'coords'")

        if name is not None:
            self.name = name





    def set_analysis_params(self, Re, alpha_start, M=None, alpha_end=None, alpha_step=None):
        """
        Set parameters for our simulation.

        :param Re: Reynolds number for the simulation.
        :param alpha_start: Starting angle of attack for the simulation. For single-AOA simulations, this is the only AOA.
        :param M: Mach number for the simulation (Optional).
        :param alpha_end: Ending angle of attack for the simulation (Optional).

        """
        if isinstance(Re, list) and isinstance(alpha_start, list) and isinstance(M, list):
            self.Re_list = Re
            self.alpha_start_list = alpha_start
            self.M_list = M
            self.alpha_end = alpha_end
            self.alpha_step = alpha_step
        else:
            self.Re = Re
            self.alpha_start = alpha_start
            self.M = M if M is not None else 0.0
            self.alpha_end = alpha_end
            self.alpha_step = alpha_step

            if alpha_end is None and alpha_step is None:
                # Single AOA simulation
                self.alpha = [alpha_start]
            elif alpha_end is not None and alpha_step is not None:
                # Multi-angle simulation (generate a list from alpha_start to alpha_end)
                # Make sure we always move in the correct direction (up or down).
                num_steps = int(abs(alpha_end - alpha_start) / alpha_step) + 1
                if alpha_end > alpha_start:
                    self.alpha = [alpha_start + i * alpha_step for i in range(num_steps)]
                else:
                    self.alpha = [alpha_start - i * alpha_step for i in range(num_steps)]
            else:
                # If alpha_end or alpha_step is given without the other, it's ambiguous
                raise ValueError("For multiple AoAs, both alpha_end and alpha_step must be provided. For a single AoA, omit both alpha_end and alpha_step.")

    def run_analysis(self, iters: int = 100):
        """
        Runs the XFOIL analysis with the airfoil and the current simulation parameters.

        :param airfoil: An Airfoil object containing name and coordinate data.
        :param iters: Number of iterations to run the simulation for.
        :return: A dictionary containing results (e.g., list of angles of attack, lift, drag, etc.)
        """

        if self.Re is None or self.alpha is None:
            raise AttributeError("Analysis parameters (Re, alpha) must be set before calling run_analysis.")

        with tempfile.TemporaryDirectory() as tmpdir:
            #1. Write airfoil coords to a file
            airfoil_file = os.path.join(tmpdir,"airfoil.dat")
            self._write_airfoil_file(airfoil_file)

            #2. Create XFOIL input script
            xfoil_input_file = os.path.join(tmpdir, "xfoil_input.in")
            xfoil_output_file = os.path.join(tmpdir, "xfoil_output.txt")

            self._write_xfoil_input_script(
                airfoil_file = airfoil_file,
                xfoil_input_file = xfoil_input_file,
                output_file = xfoil_output_file)


            #3. Run XFOIL in batch mode
            xfoil_command = ["xfoil.exe" if os.name == "nt" else "xfoil", f"<{xfoil_input_file}"]
            try:
                completed_process = subprocess.run(
                    xfoil_command,
                    check = True,
                    shell=True,
                    stdout = subprocess.PIPE,
                    stderr = subprocess.PIPE
                )
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr.decode("utf-8",errors="ignore")
                raise RuntimeError(f"XFOIL execution failed: {error_msg}"
                                   "Ensure that xfoil.exe is in the same directory as this script!")
            results = self._parse_xfoil_output(xfoil_output_file)
            return results


    def _run_single_analysis(self, Re, alpha_start, M, iters):
        self.set_analysis_params(Re, alpha_start, M, self.alpha_end, self.alpha_step)
        return self.run_analysis(iters)
    def run_multithreaded_analysis(self, iters=100):
        if not hasattr(self, 'Re_list') or not hasattr(self, 'alpha_start_list') or not hasattr(self, 'M_list'):
            raise AttributeError("Analysis parameters (Re, alpha_start, M) must be set as lists before calling run_multithreaded_analysis.")

        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._run_single_analysis, Re, alpha_start, M, iters) for Re, alpha_start, M in zip(self.Re_list, self.alpha_start_list, self.M_list)]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
        return results


    def _write_airfoil_file(self, file_path: str):
        """
        Writes the airfoil geometry to a .dat file for XFOIL.
        """
        with open(file_path, "w") as f:
            f.write(f"{self.name}\n")
            for (x, y) in self.coords:
                f.write(f"{x:.6f} {y:.6f}\n")

    def _write_xfoil_input_script(self, airfoil_file, xfoil_input_file, output_file):
        """
        Builds the XFOIL batch script to:
          1. Load airfoil geometry
          2. Set Reynolds, Mach, etc.
          3. Run single or multiple AoA
          4. Write results to the output file
        """

        commands = []

        # Load airfoil
        commands.append(f"LOAD {airfoil_file}")
        commands.append("")   # accept default name from file or empty line

        # Optional: Increase resolution of the paneling
        commands.append("PPAR")
        commands.append("N 200")  # e.g., set number of panels
        commands.append("")       # exit PPAR menu
        commands.append("")       # exit PPAR menu
        # Enter OPER menu
        commands.append("OPER")
        commands.append(f"VISC {self.Re}")
        commands.append(f"MACH {self.M:.4f}")

        # Save analyses to memory
        commands.append("PACC")
        commands.append("")
        commands.append("")


        # Single angle or sweep
        if len(self.alpha) == 1:
            alpha_val = self.alpha[0]
            commands.append(f"ALFA {alpha_val:.2f}")
        else:
            alpha_start = self.alpha[0]
            alpha_end   = self.alpha[-1]
            alpha_step  = self.alpha[1] - self.alpha[0]  # assume uniform step
            commands.append(f"ASEQ {alpha_start} {alpha_end} {alpha_step}")

        # Write out polar (PWRT)
        commands.append(f"PWRT")
        commands.append(self.name)
        commands.append("Y") # yes to overwrite (if necessary)
        commands.append("")  # blank line to finalize

        # Quit
        commands.append("QUIT")

        # Write commands to the .in file
        script_content = "\n".join(commands) + "\n"
        with open(xfoil_input_file, "w") as f:
            f.write(script_content)

    def _parse_xfoil_output(self, output_file: str):
        output_file = self.name
        """
        Parses the XFOIL output (polar data) from the specified file,
        extracting alpha, Cl, Cd, and Cm into a dictionary.

        :return: dict of lists, e.g. {
                    "alpha": [...],
                    "Cl": [...],
                    "Cd": [...],
                    "Cm": [...]
                }
        """
        if not os.path.exists(output_file):
            raise FileNotFoundError("XFOIL output file not found. The run may have failed.")

        results = {
            "alpha": [],
            "Cl": [],
            "Cd": [],
            "Cm": []
        }

        with open(output_file, "r") as f:
            in_data_section = False
            for line in f:
                # Detect header or data section
                if "alpha" in line and "CL" in line:
                    in_data_section = True
                    continue
                if in_data_section:
                    tokens = line.split()
                    if len(tokens) < 5:
                        # Not enough columns or end of data
                        continue
                    try:
                        alpha_val = float(tokens[0])
                        cl_val    = float(tokens[1])
                        cd_val    = float(tokens[2])
                        cm_val    = float(tokens[4])  # skipping CDp at tokens[3]

                        results["alpha"].append(alpha_val)
                        results["Cl"].append(cl_val)
                        results["Cd"].append(cd_val)
                        results["Cm"].append(cm_val)
                    except ValueError:
                        # Some lines may not parse cleanly
                        pass
        os.remove(self.name)
        return results

    def __repr__(self):
        return f"<Airfoil name='{self.name}' with {len(self.coords)} points>"

class Utils:
    def parse_coords(raw_text: str):
        """
        Converts multiline text of coordinates into a list of (x, y) tuples.

        :param raw_text: A string where each line has two float values separated by space.
        :return: A list of (float, float) tuples.

        Example:
            raw_data = \"\"\"1.0000     0.0013
            0.9500     0.0114
            ...
            1.0000    -0.0013\"\"\"

            coords = parse_coords(raw_data)
            # coords -> [(1.0, 0.0013), (0.95, 0.0114), ..., (1.0, -0.0013)]
            """
        # Split the text into lines
        lines = raw_text.strip().splitlines()

        # Parse each line into (x, y)
        coords = []
        for line in lines:
            if len(line) < 2:
                # Definitely not two numbers, skip
                lines = lines[1:]
                continue
            # Split by whitespace
            parts = line.split()
            if len(parts) >= 2 and not any(ch.isalpha() for ch in line):
                x_str, y_str = parts[0], parts[1]
                x_val, y_val = float(x_str), float(y_str)
                coords.append((x_val, y_val))

        return coords