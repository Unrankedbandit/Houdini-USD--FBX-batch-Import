# Batch USD and FBX Import for Houdini TOP Networks

This collection of scripts automates the process of importing multiple USD and FBX files into Houdini using PDG/TOP networks. It creates individual import nodes for each file found in the specified directory pattern.

## Setup

1. Create a TOP network in Houdini (can be inside an Object node or at root level)
2. Add a File Pattern node:
   - Set the "Pattern" parameter to your asset directory (e.g., `/path/to/assets/*.usd` or `/path/to/assets/*.fbx`)
   - Make sure the pattern points to the correct file extension for your needs
3. Add a Python Script node and connect it to the File Pattern node
4. Copy either `BatchUSDimport.py` or `BatchFBXimport.py` into the Python Script node depending on your needs

## Network Structure



## How It Works

The scripts perform the following operations:

1. Creates a geometry container node in the /obj network:
   - `usd_import` for USD files
   - `fbx_import` for FBX files

2. Reads the directory path from the File Pattern node's pattern parameter

3. For USD files:
   - Creates a `usdimport` node for each USD file
   - Names nodes using pattern: `usd_import_[filename]`
   - Sets the filepath parameter to the USD file path

4. For FBX files:
   - Creates a `file` node for each FBX file
   - Names nodes using pattern: `fbx_import_[filename]`
   - Sets the file parameter to the FBX file path

## Features

- Automatically creates geometry container nodes if they don't exist
- Prevents duplicate node creation
- Prevents continuous script looping
- Normalizes file paths for cross-platform compatibility
- Sanitizes node names (handles spaces and special characters)
- Provides detailed logging and error messages
- Supports multiple file formats:
  - USD: `.usd`, `.usda`, `.usdc`
  - FBX: `.fbx`

## Requirements

- Houdini 19.0 or later
- USD plugin installed (for USD imports)
- Python 3.x (included with Houdini)

## Usage

1. Set up your TOP network as described in the Setup section
2. Configure the File Pattern node:
   - Point to your asset directory
   - Use correct file extension (*.usd or *.fbx)
   - Ensure the path is accessible
3. Choose the appropriate script:
   - `BatchUSDimport.py` for USD files
   - `BatchFBXimport.py` for FBX files
4. The script will:
   - Create a container node if it doesn't exist
   - Create import nodes for each file
   - Skip if nodes already exist

## Node Structure


## Error Handling

The scripts include comprehensive error handling for:
- Missing or inaccessible directories
- Invalid file paths
- File permission issues
- Node creation failures
- Invalid node names
- Duplicate nodes

## Limitations and Notes

- The scripts create nodes only once to prevent duplication
- If you need to reimport, delete the existing container node
- Node names are sanitized to be Houdini-compatible
- The scripts check for existing nodes before creating new ones
- File paths are normalized to use forward slashes
- Container nodes are created in the /obj network

## Troubleshooting

1. If no nodes are created:
   - Check if the File Pattern path is correct
   - Verify files exist in the specified directory
   - Check file permissions

2. If script keeps running:
   - This is normal - the script checks for existing nodes
   - It will skip creation if nodes already exist

3. For file access issues:
   - Ensure paths are accessible
   - Check file permissions
   - Verify file extensions match the pattern

## File Organization

- Keep USD files in a dedicated directory
- Keep FBX files in a dedicated directory
- Use clear file naming conventions
- Avoid spaces and special characters in filenames
## Notes

- The scripts create all import nodes within their respective geometry containers
- Each file gets its own import node with a unique name
- Work items are tracked to prevent duplicate processing
- The scripts can run standalone in Houdini (outside PDG)
- FBX files with spaces or special characters in their names are automatically sanitized

## Support

If you encounter any issues or have questions, please:
1. Check the [Issues](https://github.com/unrankedbandit/obj_fbx_converter/issues) page
2. Create a new issue with detailed information about your problem