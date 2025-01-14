# Batch USD Import for Houdini TOP Networks

This script automates the process of importing multiple USD files into Houdini using a PDG/TOP network. It creates individual USD import nodes for each USD file found in the specified directory pattern.

## Setup

1. Create a TOP network in Houdini
2. Add a File Pattern node
   - Set the pattern to your USD directory (e.g., `$HIP/usd/*.usd`)
   - Enable "Create Work Item per File"
3. Add a Python Script node and connect it to the File Pattern node
4. Copy the `BatchUSDimport.py` script into the Python Script node

## Network Structure 


## How It Works

The script performs the following operations:

1. When executed in a PDG context:
   - Processes each work item from the File Pattern node
   - Creates a unique USD import node for each USD file
   - Names nodes using the pattern: `usd_import_[filename]_[workitem_index]`
   - Prevents duplicate processing of work items

2. When executed outside PDG:
   - Searches for USD files in the current HIP directory
   - Creates import nodes for any found USD files
   - Names nodes using the pattern: `usd_import_[filename]`

## Features

- Automatically creates a geometry container node (`usd_import`) if it doesn't exist
- Normalizes file paths for cross-platform compatibility
- Handles duplicate node creation
- Provides error handling and detailed logging
- Supports `.usd`, `.usda`, and `.usdc` file formats

## Requirements

- Houdini with USD plugin installed
- PDG/TOPs license
- Python 3.x (included with Houdini)

## Usage

1. Set up your TOP network as described in the Setup section
2. Configure the File Pattern node to point to your USD files
3. Run the TOP network
4. The script will create USD import nodes in `/obj/usd_import/`

## Error Handling

The script includes comprehensive error handling for:
- Missing USD plugin
- Invalid file paths
- Missing work item attributes
- File access issues

## Notes

- The script creates all USD import nodes within a single geometry container
- Each USD file gets its own import node with a unique name
- Work items are tracked to prevent duplicate processing
- The script can also run standalone in Houdini (outside PDG)