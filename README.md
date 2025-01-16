# Batch USD and FBX Import for Houdini TOP Networks

This collection of scripts automates the process of importing multiple USD and FBX files into Houdini using PDG/TOP networks. It creates individual import nodes for each file found in the specified directory pattern.

## Setup

1. Create a TOP network in Houdini
2. Add a File Pattern node
   - Set the pattern to your asset directory (e.g., `$HIP/usd/*.usd` or `$HIP/fbx/*.fbx`)
   - Enable "Create Work Item per File"
3. Add a Python Script node and connect it to the File Pattern node
4. Copy either `BatchUSDimport.py` or `BatchFBXimport.py` into the Python Script node depending on your needs

## Network Structure


## How It Works

The scripts perform the following operations:

1. When executed in a PDG context:
   - Processes each work item from the File Pattern node
   - Creates a unique import node for each file
   - Names nodes using the pattern: 
     - USD: `usd_import_[filename]_[workitem_index]`
     - FBX: `fbx_import_[filename]_[workitem_index]`
   - Prevents duplicate processing of work items

2. When executed outside PDG:
   - Searches for files in the specified directory
   - Creates import nodes for any found files
   - Names nodes using the pattern: 
     - USD: `usd_import_[filename]`
     - FBX: `fbx_import_[filename]`

## Features

- Automatically creates geometry container nodes (`usd_import` or `fbx_import`) if they don't exist
- Normalizes file paths for cross-platform compatibility
- Handles duplicate node creation
- Provides error handling and detailed logging
- Supports multiple file formats:
  - USD: `.usd`, `.usda`, `.usdc`
  - FBX: `.fbx`
- Sanitizes node names for FBX files (handles spaces and special characters)
- Tracks processed files to prevent reimporting

## Requirements

- Houdini with USD plugin installed (for USD imports)
- PDG/TOPs license
- Python 3.x (included with Houdini)

## Usage

1. Set up your TOP network as described in the Setup section
2. Configure the File Pattern node to point to your asset files
3. Choose the appropriate script based on your file type:
   - `BatchUSDimport.py` for USD files
   - `BatchFBXimport.py` for FBX files
4. Run the TOP network
5. The script will create import nodes in:
   - `/obj/usd_import/` for USD files
   - `/obj/fbx_import/` for FBX files

## Error Handling

The scripts include comprehensive error handling for:
- Missing plugins
- Invalid file paths
- Missing work item attributes
- File access issues
- Invalid node names (especially for FBX files with spaces/special characters)

## Notes

- The scripts create all import nodes within their respective geometry containers
- Each file gets its own import node with a unique name
- Work items are tracked to prevent duplicate processing
- The scripts can run standalone in Houdini (outside PDG)
- FBX files with spaces or special characters in their names are automatically sanitized