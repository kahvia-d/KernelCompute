import textwrap

# --- Material Definitions ---
# A simple library of material compositions for MCNP.
# In a real application, this would be much more extensive.
MATERIALS = {
    "U3Si2": {
        "id": 1,
        "definition": "m1 92235.71c 0.03 92238.71c 0.97 14000.71c 1.0" # Example: U-235, U-238, Si
    },
    "UO2": {
        "id": 2,
        "definition": "m2 92235.71c 0.05 92238.71c 0.95 8016.71c 2.0" # Example: U-235, U-238, O-16
    },
    "water": {
        "id": 3,
        "definition": "m3 1001.71c 2.0 8016.71c 1.0" # H2O
    },
    "zircaloy": {
        "id": 4,
        "definition": "m4 40000.71c 1.0" # Zirconium
    }
}

def generate_mcnp_input(
    core_radius: float,
    core_height: float,
    fuel_type: str,
    output_filename: str = "mcnp_input.inp"
):
    """
    Generates a standardized MCNP input file for a simple cylindrical reactor core.

    Args:
        core_radius (float): The radius of the reactor core in cm.
        core_height (float): The height of the reactor core in cm.
        fuel_type (str): The key for the fuel material (e.g., "U3Si2", "UO2").
        output_filename (str): The name of the file to save the input to.
    """
    if fuel_type not in MATERIALS:
        raise ValueError(f"Fuel type '{fuel_type}' not found in material library.")

    fuel_material = MATERIALS[fuel_type]
    water_material = MATERIALS["water"]

    # Using textwrap.dedent to keep the template clean and readable
    mcnp_template = textwrap.dedent(f"""\
    Cylindrical Reactor Core Model
    c --- Cell Cards ---
    c Cell_ID  Material_ID  Density  Geometry  Parameters
    1 {fuel_material['id']} -10.5     -1 2 -3 4     imp:n=1  $ Fuel region
    2 {water_material['id']}  -1.0     (1 -2 3 -4) 5 -6 imp:n=1  $ Moderator/Coolant
    3 0                     -5 6          imp:n=0  $ Outside world

    c --- Surface Cards ---
    c Surface_ID  Mnemonic  Parameters
    1 cz   {core_radius}        $ Fuel cylinder (radius)
    2 pz   {core_height / 2}    $ Fuel top plane
    3 pz   {-core_height / 2}   $ Fuel bottom plane
    4 rpp  {-core_radius-10} {core_radius+10} {-core_radius-10} {core_radius+10} {-core_height/2-10} {core_height/2+10} $ Outer boundary box
    5 pz   {core_height/2 + 10} $ Box top
    6 pz   {-core_height/2 - 10} $ Box bottom

    c --- Data Cards ---
    c Material definitions
    {fuel_material['definition']}
    {water_material['definition']}

    c Physics and Source Definition
    kcode 1000 1.0 10 110  $ K-eigenvalue calculation, 1000 neutrons/cycle
    ksrc  0 0 0            $ Source particles start at the center

    c Tallies for Neutron Flux
    c Rectangular mesh tally covering the core
    tally 4
    c Mesh geometry: Covers the whole core from -radius to +radius
    c Origin at bottom-left-rear corner of the mesh
    fmesh4:n geom=xyz origin={-core_radius} {-core_radius} {-core_height/2}
    c Define mesh intervals: 50 bins in x, 50 in y, 20 in z
    imesh4 i={core_radius*2} ni=50
    jmesh4 j={core_radius*2} nj=50
    kmesh4 k={core_height} nk=20
    c This creates a 'meshtal' file for output
    end
    """)

    with open(output_filename, "w") as f:
        f.write(mcnp_template)
    
    print(f"MCNP input file '{output_filename}' generated successfully.")
    return output_filename

if __name__ == '__main__':
    # Example usage when running the script directly
    generate_mcnp_input(core_radius=150.0, core_height=300.0, fuel_type="U3Si2")
