import os
from pxr import Usd, UsdGeom, Sdf

def extract_and_export_usd_items(usd_file_path):
    """
    Extract individual items from a USD file and export them as separate USD files.
    
    Args:
        usd_file_path (str): Path to the input USD file
    """
    # Open the USD stage
    stage = Usd.Stage.Open(usd_file_path)
    if not stage:
        print(f"Failed to open USD file: {usd_file_path}")
        return

    # Get the root layer directory
    output_dir = os.path.dirname(usd_file_path)
    base_name = os.path.splitext(os.path.basename(usd_file_path))[0]

    # Iterate through all prims in the stage
    for prim in stage.Traverse():
        if prim.IsValid():
            # Create a new stage for each prim
            new_stage = Usd.Stage.CreateNew(os.path.join(
                output_dir,
                f"{base_name}_{prim.GetName()}.usd"
            ))

            # Copy the prim to the new stage
            new_stage.DefinePrim(prim.GetPath().pathString, prim.GetTypeName())
            new_stage.GetRootLayer().TransferContent(
                stage.GetRootLayer(),
                prim.GetPath()
            )

            # Save the new stage
            new_stage.Save()
            print(f"Exported: {prim.GetName()}")

if __name__ == "__main__":
    usd_file_path = "C:/Users/Sputnik/Desktop/USDtest/Modular_Fantasy_House.usdz"
    extract_and_export_usd_items(usd_file_path)
