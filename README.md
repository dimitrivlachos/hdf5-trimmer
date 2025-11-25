# HDF5 Trimmer

A simple Python script to trim HDF5 files to a specific number of rows or a range of rows.

## Quick Start

1. **Create the local Mamba environment:**
   ```bash
   mamba env create -f environment.yml -p ./ENV
   ```

2. **Activate the environment:**
   ```bash
   mamba activate ./ENV
   ```

3. **Run the script:**
   ```bash
   # Trim to first 100 rows
   python trim_hdf5.py input.h5 output.h5 --rows 100
   
   # Trim to rows 50-150
   python trim_hdf5.py input.h5 output.h5 --range 50 150
   ```

## Usage

### Trim to first N rows
```bash
python trim_hdf5.py input.h5 output.h5 --rows 100
```

### Trim to a specific range
```bash
python trim_hdf5.py input.h5 output.h5 --range 50 150
```

## Arguments

- `input`: Path to the input HDF5 file
- `output`: Path for the output trimmed HDF5 file
- `--rows N` or `-r N`: Keep only the first N rows
- `--range START END` or `-R START END`: Keep rows from START to END

## Notes

- The script preserves dataset attributes and compression settings
- All datasets in the HDF5 file are trimmed to the same range
- The output file will be created (or overwritten if it exists)
- The environment is installed locally in the `ENV/` directory (not added to git)

## Deactivate Environment

```bash
mamba deactivate
```
