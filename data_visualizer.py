import numpy as np
import matplotlib.pyplot as plt

def parse_meshtal(meshtal_file: str) -> np.ndarray:
    """
    Parses the MCNP 'meshtal' file to extract the 3D flux data.

    Args:
        meshtal_file (str): Path to the 'meshtal' file.

    Returns:
        A 3D numpy array containing the neutron flux data (x, y, z).
    """
    with open(meshtal_file, 'r') as f:
        lines = f.readlines()

    # Find where the data block begins
    data_start_line = 0
    for i, line in enumerate(lines):
        if "Energy" in line and "Rel Error" in line:
            data_start_line = i + 1
            break

    # Extract data values
    flux_data = []
    for line in lines[data_start_line:]:
        parts = line.split()
        if len(parts) >= 8: # A data line should have at least this many parts
            flux_data.append(float(parts[7]))

    # Find dimensions from the header (a bit of parsing logic)
    nx, ny, nz = 0, 0, 0
    for line in lines:
        if "X direction" in line:
            nx = int(line.split()[-1])
        if "Y direction" in line:
            ny = int(line.split()[-1])
        if "Z direction" in line:
            nz = int(line.split()[-1])
        if nx > 0 and ny > 0 and nz > 0:
            break
            
    if nx * ny * nz == 0:
        raise ValueError("Could not determine mesh dimensions from meshtal file.")

    # Reshape the flat list of data into a 3D numpy array
    flux_array = np.array(flux_data).reshape((nx, ny, nz))
    return flux_array

def plot_flux_distributions(flux_data: np.ndarray, core_radius: float, core_height: float) -> (str, str):
    """
    Generates and saves radial and axial flux distribution plots.

    Args:
        flux_data (3D np.ndarray): The parsed flux data.
        core_radius (float): The radius of the core for axis labeling.
        core_height (float): The height of the core for axis labeling.

    Returns:
        A tuple with the file paths of the generated plots (radial_plot_path, axial_plot_path).
    """
    nx, ny, nz = flux_data.shape

    # 1. Radial Distribution (a slice through the middle, z-axis)
    radial_flux = flux_data[:, :, nz // 2]
    plt.figure(figsize=(8, 7))
    plt.imshow(
        radial_flux.T, # Transpose to match (x,y) conventional plot
        extent=[-core_radius, core_radius, -core_radius, core_radius],
        origin='lower',
        cmap='viridis'
    )
    plt.colorbar(label='Neutron Flux (arbitrary units)')
    plt.xlabel('X (cm)')
    plt.ylabel('Y (cm)')
    plt.title('Radial Neutron Flux Distribution (Core Midplane)')
    plt.grid(True, alpha=0.2)
    radial_plot_path = 'radial_flux.png'
    plt.savefig(radial_plot_path)
    plt.close()
    print(f"Radial plot saved to {radial_plot_path}")

    # 2. Axial Distribution (a slice through the center, y-axis)
    axial_flux = flux_data[nx // 2, :, :]
    plt.figure(figsize=(7, 8))
    plt.imshow(
        axial_flux.T, # Transpose to match (y,z) convention
        extent=[-core_radius, core_radius, -core_height/2, core_height/2],
        origin='lower',
        cmap='viridis',
        aspect='auto'
    )
    plt.colorbar(label='Neutron Flux (arbitrary units)')
    plt.xlabel('Y (cm)')
    plt.ylabel('Z (cm)')
    plt.title('Axial Neutron Flux Distribution (Core Centerline)')
    plt.grid(True, alpha=0.2)
    axial_plot_path = 'axial_flux.png'
    plt.savefig(axial_plot_path)
    plt.close()
    print(f"Axial plot saved to {axial_plot_path}")

    return radial_plot_path, axial_plot_path

if __name__ == '__main__':
    # Example: Assumes a 'meshtal' file exists in the current directory
    try:
        flux = parse_meshtal('meshtal')
        plot_flux_distributions(flux, core_radius=150.0, core_height=300.0)
    except FileNotFoundError:
        print("Error: 'meshtal' file not found. Run a calculation first.")
    except Exception as e:
        print(f"An error occurred: {e}")