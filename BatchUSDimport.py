#v 2
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

def get_filepattern_directory():
    """Get the directory path from the connected File Pattern node"""
    try:
        # Get the current TOP node
        current_node = hou.pwd()
        if not current_node:
            print("Warning: Could not get current node context")
            return None
            
        # Get the input connections
        input_nodes = current_node.inputConnections()
        if not input_nodes:
            print("Warning: No input connections found")
            return None
            
        # Get the input node
        input_node = input_nodes[0].inputNode()
        if not input_node:
            print("Warning: No input node found")
            return None
            
        print(f"Input node type: {input_node.type().name()}")
        
        if input_node.type().name() != "filepattern":
            print("Warning: Input node is not a filepattern node")
            return None
            
        # Debug: Print all parameters of the filepattern node
        print("\nAvailable parameters in File Pattern node:")
        for parm in input_node.parms():
            print(f"- {parm.name()}: {parm.description()}")
        
        # Try different possible parameter names
        possible_params = ['file', 'pattern', 'filepattern', 'File']
        file_parm = None
        
        for param_name in possible_params:
            temp_parm = input_node.parm(param_name)
            if temp_parm:
                file_parm = temp_parm
                print(f"\nFound parameter: {param_name}")
                break
                
        if not file_parm:
            print("Warning: Could not find file pattern parameter")
            return None
            
        # Evaluate the file pattern
        file_pattern = file_parm.eval()
        print(f"File pattern: {file_pattern}")
        
        if not file_pattern:
            print("Warning: File pattern is empty")
            return None
            
        # Extract the directory from the file pattern
        directory_path = os.path.dirname(file_pattern)
        if not directory_path:
            print("Warning: Could not extract directory from file pattern")
            return None
            
        normalized_path = normalize_path(directory_path)
        print(f"Found directory path: {normalized_path}")
        return normalized_path
        
    except Exception as e:
        print(f"Error getting File Pattern directory: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def process_usd_files():
    """Main function to process USD files"""
    try:
        # Get the current work item
        current_item = pdg.workItem()
        
        if current_item:
            try:
                # Create a unique key for this work item
                work_item_key = f"processed_work_item_{current_item.index}"
                
                # Check if we've already processed this work item
                if not hasattr(hou.session, work_item_key):
                    # Get the file path from the work item
                    usd_file = normalize_path(current_item.stringAttribValue("file"))
                    if not usd_file:
                        raise ValueError("'file' attribute is empty")
                    
                    # If the path is not absolute, combine it with the File Pattern directory
                    if not os.path.isabs(usd_file):
                        filepattern_dir = get_filepattern_directory()
                        if filepattern_dir:
                            usd_file = os.path.join(filepattern_dir, usd_file)
                            usd_file = normalize_path(usd_file)
                        
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
            # If running outside PDG, use the File Pattern directory if available
            directory_path = get_filepattern_directory()
            if not directory_path:
                print("Warning: Could not get directory from File Pattern node")
                directory_path = normalize_path(hou.expandString("$HIP"))
                print("Falling back to HIP directory")
            
            print(f"Using directory: {directory_path}")
            
            if not os.path.exists(directory_path):
                print(f"Error: Directory does not exist: {directory_path}")
                return
                
            # Look for any .usd files in the directory
            usd_files = [f for f in os.listdir(directory_path) if f.endswith(('.usd', '.usda', '.usdc'))]
            
            if not usd_files:
                print(f"No USD files found in {directory_path}")
                return
                
            print(f"Found {len(usd_files)} USD files")
            for usd_file in usd_files:
                file_path = normalize_path(os.path.join(directory_path, usd_file))
                print(f"Processing USD file: {file_path}")
                create_usd_import(file_path)

    except ImportError as e:
        print("Error importing modules:", str(e))
    except Exception as e:
        print("Error during execution:", str(e))
        raise  # Re-raise the exception to see the full stack trace

# Execute the main function
process_usd_files()