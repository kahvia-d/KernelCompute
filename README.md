# Reactor Core Neutron Flux Calculation Tool

This project provides an automated toolchain for calculating and visualizing neutron flux in a simplified reactor core model using MCNP. It is designed to be controlled via a simple REST API, which can be integrated into other platforms like Coze.

## Project Structure

- `mcnp_generator.py`: Generates MCNP input files from parameters.
- `task_runner.py`: Executes MCNP simulations.
- `data_visualizer.py`: Parses MCNP output and creates flux plots.
- `api.py`: A Flask web server that exposes the functionality via a REST API.
- `runs/`: A directory where the results of each calculation are stored.

## Prerequisites

1.  **Python 3.8+**: Make sure you have Python installed.
2.  **MCNP**: You must have a working installation of MCNP (e.g., MCNP6). The MCNP executable must be in your system's `PATH`. You can verify this by opening a terminal and typing `mcnp6 --version` (or your specific executable name).
3.  **Python Libraries**: Install the required libraries using pip:
    ```bash
    pip install Flask numpy matplotlib
    ```

## How to Run

1.  **Start the API Server**:
    Open a terminal in the project directory and run the Flask app:
    ```bash
    python api.py
    ```
    The server will start, by default on `http://127.0.0.1:5000`.

2.  **Submit a Calculation Task**:
    Use a tool like `curl` or any API client to send a `POST` request to the `/calculate` endpoint.

    **Example using `curl`:**
    ```bash
    curl -X POST -H "Content-Type: application/json" \
    -d '{
        "core_radius": 150.0,
        "core_height": 300.0,
        "fuel_type": "U3Si2"
    }' \
    http://127.0.0.1:5000/calculate
    ```
    Available `fuel_type` options are currently `U3Si2` and `UO2`.

3.  **View the Results**:
    If the calculation is successful, the API will return a JSON response containing links to the output plots.

    **Example successful response:**
    ```json
    {
      "status": "success",
      "run_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "message": "Calculation complete. Plots generated.",
      "plots": {
        "radial": "/results/a1b2c3d4-e5f6-7890-abcd-ef1234567890/radial_flux.png",
        "axial": "/results/a1b2c3d4-e5f6-7890-abcd-ef1234567890/axial_flux.png"
      }
    }
    ```
    You can then open these URLs in your browser to see the plots:
    - `http://127.0.0.1:5000/results/a1b2c3d4-e5f6-7890-abcd-ef1234567890/radial_flux.png`
    - `http://127.0.0.1:5000/results/a1b2c3d4-e5f6-7890-abcd-ef1234567890/axial_flux.png`

## Integration with Coze

In Coze, you can create a custom tool (plugin) that calls this API.

1.  **Define the Tool**: Set up a new tool in Coze that points to your API's endpoint (`http://<your-computer-ip>:5000/calculate`).
2.  **Input Parameters**: Define the input parameters for the tool: `core_radius` (number), `core_height` (number), and `fuel_type` (string).
3.  **Orchestration**: Create a bot that prompts the user for these parameters, calls your new tool, and then displays the resulting images from the URLs provided in the API response.