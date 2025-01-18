#v 2
import hou
import pdg
import os

def normalize_path(path):
    """Convert path to use forward slashes consistently"""
    return path.replace('\\', '/')

def create_fbx_import(file_path, work_item=None):
    """Create FBX import node with the given file path"""
    # Normalize the file path
    file_path = normalize_path(file_path)
    
    # Access or create the /obj network
    obj_net = hou.node("/obj")
    if obj_net is None:
        raise RuntimeError("Cannot access /obj network")
        
    # Create or get the geometry container
    geo_name = "fbx_import"
    fbx_import_node = obj_net.node(geo_name)
    if fbx_import_node is None:
        fbx_import_node = obj_net.createNode(
            "geo", node_name=geo_name, run_init_scripts=False
        )
        fbx_import_node.moveToGoodPosition()

    try:
        # Extract the file name from the path
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Create a unique name for each FBX import node
        if work_item:
            fbx_node_name = f"fbx_import_{file_name}_{work_item.index}"
        else:
            fbx_node_name = f"fbx_import_{file_name}"
            
        # Check if node already exists - if it does, don't recreate it
        existing_node = fbx_import_node.node(fbx_node_name)
        if existing_node:
            print(f"Node {fbx_node_name} already exists, skipping creation")
            return existing_node

        # Create File node for FBX import
        fbx_node = fbx_import_node.createNode("file", fbx_node_name)
        
        # Verify the file exists before setting it
        if not os.path.exists(file_path):
            print(f"Warning: FBX file does not exist: {file_path}")
            
        fbx_node.parm("file").set(file_path)
        fbx_node.moveToGoodPosition()
        
        print(f"Created FBX import node: {fbx_node_name} with file: {file_path}")
        return fbx_node
        
    except hou.OperationFailed:
        raise RuntimeError("Failed to create FBX import node.")

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

def process_fbx_files():
    """Main function to process FBX files"""
    try:
        # Check if we already have a container with nodes
        container = hou.node("/obj/fbx_import")
        if container and len(container.children()) > 0:
            print("FBX nodes already exist, skipping import")
            return
            
        # Get directory from File Pattern node
        directory_path = get_filepattern_directory()
        if not directory_path:
            print("Could not get directory from File Pattern node")
            return
            
        print(f"Processing directory: {directory_path}")
        
        # Debug: List all files in directory
        try:
            all_files = os.listdir(directory_path)
            print(f"\nAll files in directory:")
            for f in all_files:
                print(f"- {f}")
            
            # Find FBX files
            fbx_files = [f for f in all_files if f.lower().endswith('.fbx')]
            
            if not fbx_files:
                print(f"\nNo FBX files found in {directory_path}")
                print("Note: FBX extension check is case-sensitive, checking for '.fbx'")
                return
                
            print(f"\nFound {len(fbx_files)} FBX files:")
            for fbx_file in sorted(fbx_files):
                file_path = os.path.join(directory_path, fbx_file)
                print(f"Processing FBX file: {file_path}")
                create_fbx_import(file_path)

        except Exception as e:
            print(f"Error accessing directory: {str(e)}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"Error processing files: {str(e)}")

# Execute the main function
process_fbx_files()
