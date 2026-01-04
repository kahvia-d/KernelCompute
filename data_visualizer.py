import os
import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt

def parse_meshtal(meshtal_file: str) -> np.ndarray:
    """
    Parses the MCNP 'meshtal' file to extract the 3D flux data.
    """
    with open(meshtal_file, 'r') as f:
        lines = f.readlines()

    # Find where the data block begins
    data_start_line = 0
    # A more robust way to find the start of data
    for i, line in enumerate(lines):
        # Look for a line that looks like a data header
        if "Tally" in line and "Rel Error" in line:
            data_start_line = i + 1
            break

    # Extract data values
    flux_data = []
    for line in lines[data_start_line:]:
        parts = line.split()
        if len(parts) >= 4: # A data line should have at least this many parts
            # In our fake data, the flux is the 4th value (index 3)
            try:
                flux_data.append(float(parts[3]))
            except (ValueError, IndexError):
                # Ignore lines that don't contain valid data
                continue

    # Find dimensions from the header
    nx, ny, nz = 0, 0, 0
    for line in lines:
        if "X direction" in line:
            # !! 修改在这里: 从 [-1] 改为 [-2] !!
            nx = int(line.split()[-2]) 
        if "Y direction" in line:
            # !! 修改在这里: 从 [-1] 改为 [-2] !!
            ny = int(line.split()[-2])
        if "Z direction" in line:
            # !! 修改在这里: 从 [-1] 改为 [-2] !!
            nz = int(line.split()[-2])
        if nx > 0 and ny > 0 and nz > 0:
            break
            
    if nx * ny * nz == 0 or len(flux_data) != nx * ny * nz:
        raise ValueError(f"Could not parse mesh dimensions or data mismatch. Found dims ({nx},{ny},{nz}) and {len(flux_data)} data points.")

    # Reshape the flat list of data into a 3D numpy array
    # The order MCNP writes is X, then Y, then Z. Numpy's reshape order is similar.
    # However, meshtal files often list Z, then Y, then X. Let's assume C-style order for reshape.
    flux_array = np.array(flux_data).reshape((nz, ny, nx))
    # We need to swap axes to get it into (nx, ny, nz) for our plotting logic
    flux_array = np.transpose(flux_array, (2, 1, 0))
    
    return flux_array
        
def plot_flux_distributions(flux_data: np.ndarray, core_radius: float, core_height: float, output_dir: str) -> (str, str):
    """
    Generates and saves radial and axial flux distribution plots into a specific directory.

    Args:
        flux_data (3D np.ndarray): The parsed flux data.
        core_radius (float): The radius of the core for axis labeling.
        core_height (float): The height of the core for axis labeling.
        output_dir (str): The directory where the plots should be saved.

    Returns:
        A tuple with the absolute file paths of the generated plots.
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    nx, ny, nz = flux_data.shape

    # 1. Radial Distribution
    radial_flux = flux_data[:, :, nz // 2]
    plt.figure(figsize=(8, 7))
    plt.imshow(
        radial_flux.T,
        extent=[-core_radius, core_radius, -core_radius, core_radius],
        origin='lower',
        cmap='viridis'
    )
    plt.colorbar(label='Neutron Flux (arbitrary units)')
    plt.xlabel('X (cm)')
    plt.ylabel('Y (cm)')
    plt.title('Radial Neutron Flux Distribution (Core Midplane)')
    plt.grid(True, alpha=0.2)

    # !! 修改在这里: 将文件保存到指定的 output_dir 目录中 !!
    radial_plot_path = os.path.join(output_dir, 'radial_flux.png')
    plt.savefig(radial_plot_path)
    plt.close()
    print(f"Radial plot saved to {radial_plot_path}")

    # 2. Axial Distribution
    # Slice through the center, showing the Z-X plane
    axial_flux = flux_data[:, ny // 2, :]
    plt.figure(figsize=(7, 8))
    plt.imshow(
        axial_flux.T,
        extent=[-core_radius, core_radius, -core_height/2, core_height/2],
        origin='lower',
        cmap='viridis',
        aspect='auto'
    )
    plt.colorbar(label='Neutron Flux (arbitrary units)')
    plt.xlabel('X (cm)')
    plt.ylabel('Z (cm)')
    plt.title('Axial Neutron Flux Distribution (Core Centerline)')
    plt.grid(True, alpha=0.2)

    # !! 修改在这里: 将文件保存到指定的 output_dir 目录中 !!
    axial_plot_path = os.path.join(output_dir, 'axial_flux.png')
    plt.savefig(axial_plot_path)
    plt.close()
    print(f"Axial plot saved to {axial_plot_path}")

    # 返回图片的绝对路径
    return os.path.abspath(radial_plot_path), os.path.abspath(axial_plot_path)

if __name__ == '__main__':
    # Example: Assumes a 'meshtal' file exists in the current directory
    try:
        flux = parse_meshtal('meshtal')
        plot_flux_distributions(flux, core_radius=150.0, core_height=300.0)
    except FileNotFoundError:
        print("Error: 'meshtal' file not found. Run a calculation first.")
    except Exception as e:
        print(f"An error occurred: {e}")