#v 2
import hou
import pdg
import os

def normalize_path(path):
    """Convert path to use forward slashes consistently"""
    return path.replace('\\', '/')

def sanitize_node_name(name):
    """Convert a string into a valid Houdini node name"""
    sanitized = name.replace(' ', '_')
    sanitized = ''.join(c for c in sanitized if c.isalnum() or c == '_')
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"
    return sanitized

def get_filepattern_directory():
    """Get the directory path from the connected File Pattern node"""
    try:
        current_node = hou.pwd()
        if not current_node:
            return None
            
        input_nodes = current_node.inputConnections()
        if not input_nodes:
            return None
            
        input_node = input_nodes[0].inputNode()
        if not input_node or input_node.type().name() != "filepattern":
            return None
            
        pattern_parm = input_node.parm("pattern")
        if not pattern_parm:
            return None
            
        file_pattern = pattern_parm.eval()
        return normalize_path(os.path.dirname(file_pattern))
        
    except Exception as e:
        print(f"Error getting File Pattern directory: {str(e)}")
        return None

def create_usd_import(file_path):
    """Create USD import node with the given file path"""
    try:
        # Create the container node if it doesn't exist
        container = hou.node("/obj/usd_import")
        if not container:
            container = hou.node("/obj").createNode("geo", "usd_import")
            print("Created container node: /obj/usd_import")
            
        # Generate node name from file name
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        node_name = f"usd_import_{sanitize_node_name(base_name)}"
            
        # Check if node already exists
        if container.node(node_name):
            print(f"Node {node_name} already exists, skipping creation")
            return None
            
        # Create and configure USD import node
        usd_node = container.createNode("usdimport", node_name)
        usd_node.parm("filepath1").set(normalize_path(file_path))
        usd_node.setDisplayFlag(True)
        usd_node.setRenderFlag(True)
        usd_node.moveToGoodPosition()
        
        print(f"Created USD import node: {node_name}")
        return usd_node
        
    except Exception as e:
        print(f"Error creating USD import node: {str(e)}")
        return None

def process_usd_files():
    """Main function to process USD files"""
    try:
        # Check if we already have a container with nodes
        container = hou.node("/obj/usd_import")
        if container and len(container.children()) > 0:
            print("USD nodes already exist, skipping import")
            return
            
        # Get directory from File Pattern node
        dir_path = get_filepattern_directory()
        if not dir_path:
            print("Could not get directory from File Pattern node")
            return
            
        print(f"Processing directory: {dir_path}")
        
        # Find USD files
        if not os.path.exists(dir_path):
            print(f"Directory does not exist: {dir_path}")
            return
            
        # Updated to include .usdz files
        usd_files = [f for f in os.listdir(dir_path) if f.endswith(('.usd', '.usda', '.usdc', '.usdz'))]
        if not usd_files:
            print(f"No USD files found in {dir_path}")
            return
            
        print(f"Found {len(usd_files)} USD files")
        
        # Create the container node if it doesn't exist
        container = hou.node("/obj/usd_import")
        if not container:
            container = hou.node("/obj").createNode("geo", "usd_import")
            print("Created container node: /obj/usd_import")
        
        # Process each file
        for usd_file in sorted(usd_files):
            file_path = os.path.join(dir_path, usd_file)
            create_usd_import(file_path)

    except Exception as e:
        print(f"Error processing files: {str(e)}")

# Execute the main function
process_usd_files()