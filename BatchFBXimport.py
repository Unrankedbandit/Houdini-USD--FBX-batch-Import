import hou
import pdg
import os

# Global set to track processed files
if not hasattr(hou.session, 'processed_fbx_files'):
    hou.session.processed_fbx_files = set()

def normalize_path(path):
    """Convert path to use forward slashes consistently"""
    return path.replace('\\', '/')

def sanitize_node_name(name):
    """Convert a string into a valid Houdini node name"""
    # Replace spaces and special characters with underscores
    sanitized = name.replace(' ', '_')
    # Remove any characters that aren't alphanumeric or underscore
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
    # Ensure the name starts with a letter or underscore (Houdini requirement)
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"
    return sanitized

def create_fbx_import(file_path, work_item=None):
    """Create FBX import node with the given file path"""
    # Check if this file has already been processed
    normalized_path = normalize_path(file_path)
    if normalized_path in hou.session.processed_fbx_files:
        print(f"File already processed, skipping: {normalized_path}")
        return None
        
    # Add to processed set
    hou.session.processed_fbx_files.add(normalized_path)
    
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
        # Extract the file name from the path and sanitize it
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        file_name = sanitize_node_name(file_name)
        
        # Create a unique name for each FBX import node
        if work_item:
            fbx_node_name = f"fbx_import_{file_name}_{work_item.index}"
        else:
            fbx_node_name = f"fbx_import_{file_name}"
            
        # Ensure the node name is valid
        fbx_node_name = sanitize_node_name(fbx_node_name)
            
        # Check if node already exists - if it does, don't recreate it
        existing_node = fbx_import_node.node(fbx_node_name)
        if existing_node:
            print(f"Node {fbx_node_name} already exists, skipping creation")
            return existing_node

        # Create a File node for FBX import
        fbx_node = fbx_import_node.createNode("file", fbx_node_name)
        
        # Verify the file exists before setting it
        if not os.path.exists(file_path):
            print(f"Warning: FBX file does not exist: {file_path}")
            fbx_node.destroy()
            hou.session.processed_fbx_files.remove(normalized_path)  # Remove from processed set if failed
            return None
            
        # Set the file path
        fbx_node.parm("file").set(file_path)
        
        # Set up FBX-specific parameters
        if fbx_node.parm("missingframe"):
            fbx_node.parm("missingframe").set(1)  # Error on missing frames
            
        # Set display and render flags
        fbx_node.setDisplayFlag(True)
        fbx_node.setRenderFlag(True)
        
        # Move to a good position in the network
        fbx_node.moveToGoodPosition()
        
        print(f"Created FBX import node: {fbx_node_name} with file: {file_path}")
        return fbx_node
        
    except hou.OperationFailed as e:
        print(f"Error creating node: {str(e)}")
        hou.session.processed_fbx_files.remove(normalized_path)  # Remove from processed set if failed
        raise RuntimeError(f"Failed to create FBX import node: {str(e)}")

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
        # Get the current work item
        current_item = pdg.workItem()
        
        if current_item:
            try:
                # Create a unique key for this work item
                work_item_key = f"processed_work_item_{current_item.index}"
                
                # Check if we've already processed this work item
                if not hasattr(hou.session, work_item_key):
                    # Get the file path from the work item
                    fbx_file = normalize_path(current_item.stringAttribValue("file"))
                    if not fbx_file:
                        raise ValueError("'file' attribute is empty")
                    
                    # If the path is not absolute, combine it with the File Pattern directory
                    if not os.path.isabs(fbx_file):
                        filepattern_dir = get_filepattern_directory()
                        if filepattern_dir:
                            fbx_file = os.path.join(filepattern_dir, fbx_file)
                            fbx_file = normalize_path(fbx_file)
                        
                    print(f"\nProcessing Work Item {current_item.index}")
                    print(f"File: {fbx_file}")
                    print(f"ID: {current_item.id}")
                    
                    # Create a FBX import node for this work item
                    create_fbx_import(fbx_file, current_item)
                    
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
                
            # Look for any FBX files in the directory
            fbx_files = [f for f in os.listdir(directory_path) if f.endswith('.fbx')]
            
            if not fbx_files:
                print(f"No FBX files found in {directory_path}")
                return
                
            print(f"Found {len(fbx_files)} FBX files")
            for fbx_file in fbx_files:
                file_path = normalize_path(os.path.join(directory_path, fbx_file))
                print(f"Processing FBX file: {file_path}")
                create_fbx_import(file_path)

    except ImportError as e:
        print("Error importing modules:", str(e))
    except Exception as e:
        print("Error during execution:", str(e))
        raise  # Re-raise the exception to see the full stack trace

# Execute the main function
process_fbx_files() 