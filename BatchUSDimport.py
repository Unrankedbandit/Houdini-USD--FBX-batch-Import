import hou
import pdg
import os

def normalize_path(path):
    """Convert path to use forward slashes consistently"""
    return path.replace('\\', '/')

def create_usd_import(file_path, work_item=None):
    """Create USD import node with the given file path"""
    # Normalize the file path
    file_path = normalize_path(file_path)
    
    # Access or create the /obj network
    obj_net = hou.node("/obj")
    if obj_net is None:
        raise RuntimeError("Cannot access /obj network")
        
    # Create or get the geometry container
    geo_name = "usd_import"
    usd_import_node = obj_net.node(geo_name)
    if usd_import_node is None:
        usd_import_node = obj_net.createNode(
            "geo", node_name=geo_name, run_init_scripts=False
        )
        usd_import_node.moveToGoodPosition()

    try:
        # Extract the file name from the path
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Create a unique name for each USD import node
        if work_item:
            usd_node_name = f"usd_import_{file_name}_{work_item.index}"
        else:
            usd_node_name = f"usd_import_{file_name}"
            
        # Check if node already exists - if it does, don't recreate it
        existing_node = usd_import_node.node(usd_node_name)
        if existing_node:
            print(f"Node {usd_node_name} already exists, skipping creation")
            return existing_node

        # Create USD Import node
        usd_node = usd_import_node.createNode("usdimport", usd_node_name)
        
        # Verify the file exists before setting it
        if not os.path.exists(file_path):
            print(f"Warning: USD file does not exist: {file_path}")
            
        usd_node.parm("filepath1").set(file_path)
        usd_node.moveToGoodPosition()
        
        print(f"Created USD import node: {usd_node_name} with file: {file_path}")
        return usd_node
        
    except hou.OperationFailed:
        raise RuntimeError("Failed to create USD import node. Make sure the USD plugin is properly installed.")

try:
    # Get the current work item
    current_item = pdg.workItem()
    
    if current_item:
        try:
            # Create a unique key for this work item
            work_item_key = f"processed_work_item_{current_item.index}"
            
            # Check if we've already processed this work item
            if not hasattr(hou.session, work_item_key):
                # Process the current work item
                usd_file = normalize_path(current_item.stringAttribValue("file"))
                if not usd_file:
                    raise ValueError("'file' attribute is empty")
                    
                print(f"\nProcessing Work Item {current_item.index}")
                print(f"File: {usd_file}")
                print(f"ID: {current_item.id}")
                
                # Create a USD import node for this work item
                create_usd_import(usd_file, current_item)
                
                # Mark this work item as processed
                setattr(hou.session, work_item_key, True)
            else:
                print(f"Work item {current_item.index} has already been processed, skipping")
            
        except Exception as e:
            print(f"Error processing work item {current_item.index}: {str(e)}")
            
    else:
        # If running outside PDG, look for USD files in the HIP directory
        hip_path = normalize_path(hou.expandString("$HIP"))
        print(f"Current HIP directory: {hip_path}")
        
        # Look for any .usd files in the HIP directory
        usd_files = [f for f in os.listdir(hip_path) if f.endswith(('.usd', '.usda', '.usdc'))]
        
        if usd_files:
            for usd_file in usd_files:
                file_path = normalize_path(os.path.join(hip_path, usd_file))
                print(f"Processing USD file: {file_path}")
                create_usd_import(file_path)
        else:
            print(f"No USD files found in {hip_path}")
            print("Please specify a valid USD file path")

except ImportError as e:
    print("Error importing modules:", str(e))
except Exception as e:
    print("Error during execution:", str(e))
    raise  # Re-raise the exception to see the full stack trace
