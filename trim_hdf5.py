"""
Script to trim HDF5 files to a specific number of rows or a range of rows.
"""
import argparse
import h5py
import sys
from pathlib import Path


def trim_hdf5(input_file, output_file, start=0, end=None, force=False):
    """
    Trim an HDF5 file to a specific range of rows.
    
    Args:
        input_file: Path to input HDF5 file
        output_file: Path to output HDF5 file
        start: Starting row index (default: 0)
        end: Ending row index (default: None, means all rows from start)
        force: Whether to overwrite existing output file (default: False)
    """
    # Check if output file exists and force flag is not set
    if Path(output_file).exists() and not force:
        print(f"Error: Output file '{output_file}' already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)
    
    try:
        with h5py.File(input_file, 'r') as src:
            with h5py.File(output_file, 'w') as dst:
                # Copy attributes
                for key, value in src.attrs.items():
                    dst.attrs[key] = value
                
                # Recursive function to copy the entire hierarchy
                def copy_structure(src_group, dst_group, path=""):
                    # Iterate through items in the source group
                    for key in src_group.keys():
                        src_item = src_group[key]
                        item_path = f"{path}/{key}" if path else key
                        
                        if isinstance(src_item, h5py.Group):
                            # Create group in destination and copy its attributes
                            dst_grp = dst_group.create_group(key)
                            for attr_key, attr_value in src_item.attrs.items():
                                dst_grp.attrs[attr_key] = attr_value
                            
                            # Recursively copy the group's contents
                            copy_structure(src_item, dst_grp, item_path)
                            
                        elif isinstance(src_item, h5py.Dataset):
                            try:
                                if len(src_item.shape) > 0 and src_item.shape[0] > 0:
                                    # Determine the end index
                                    actual_end = end if end is not None else src_item.shape[0]
                                    
                                    # Only trim if we're actually reducing the size
                                    if actual_end < src_item.shape[0]:
                                        # Trim the dataset
                                        trimmed_data = src_item[start:actual_end]
                                        
                                        # Create new dataset with trimmed data
                                        dst_group.create_dataset(key, data=trimmed_data, 
                                                               compression=src_item.compression,
                                                               compression_opts=src_item.compression_opts)
                                        
                                        # Copy dataset attributes
                                        for attr_key, attr_value in src_item.attrs.items():
                                            dst_group[key].attrs[attr_key] = attr_value
                                        
                                        print(f"Trimmed '{item_path}': {src_item.shape[0]} -> {trimmed_data.shape[0]} rows")
                                    else:
                                        # Copy entire dataset (no trimming needed)
                                        data = src_item[:]
                                        dst_group.create_dataset(key, data=data, 
                                                               compression=src_item.compression,
                                                               compression_opts=src_item.compression_opts)
                                        
                                        # Copy dataset attributes
                                        for attr_key, attr_value in src_item.attrs.items():
                                            dst_group[key].attrs[attr_key] = attr_value
                                        
                                        print(f"Copied '{item_path}': {src_item.shape[0]} rows (no trimming)")
                                else:
                                    # Copy scalar datasets as-is
                                    dst_group.create_dataset(key, data=src_item[()])
                                    for attr_key, attr_value in src_item.attrs.items():
                                        dst_group[key].attrs[attr_key] = attr_value
                            except Exception as e:
                                print(f"Warning: Could not copy dataset '{item_path}': {e}")
                                # Continue processing other datasets
                
                # Start recursive copy from root
                copy_structure(src, dst)
        
        print(f"\nSuccessfully created trimmed file: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Trim HDF5 files to first N rows or a range of rows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Trim to first 100 rows
  python trim_hdf5.py input.h5 output.h5 --rows 100
  
  # Trim to rows 50-150
  python trim_hdf5.py input.h5 output.h5 --range 50 150
        """
    )
    
    parser.add_argument('input', type=str, help='Input HDF5 file')
    parser.add_argument('output', type=str, help='Output HDF5 file')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-r', '--rows', type=int, 
                      help='Number of rows from the start (e.g., --rows 100)')
    group.add_argument('-R', '--range', nargs=2, type=int, metavar=('START', 'END'),
                      help='Range of rows to extract (e.g., --range 50 150)')
    
    parser.add_argument('-f', '--force', action='store_true',
                      help='Force overwrite if output file already exists')
    
    args = parser.parse_args()
    
    # Check input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    # Determine start and end indices
    if args.rows:
        start = 0
        end = args.rows
    else:  # args.range
        start = args.range[0]
        end = args.range[1]
        if start >= end:
            print("Error: START must be less than END in range", file=sys.stderr)
            sys.exit(1)
    
    print(f"Trimming '{args.input}' from row {start} to {end}...")
    trim_hdf5(args.input, args.output, start, end, force=args.force)


if __name__ == '__main__':
    main()
