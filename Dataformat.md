# Vibrana Data Format

This document describes how data is stored and transformed in the Vibrana prototype.

### Data Hierarchy
Vibrana is designed to work with multiple datasets. Each dataset contains multiple subsets, which are divided into chunks.
This is easier to demonstrate with an example:
* dataset: Hydro Power Plant Vibrations
* subsets: Vibrations in X, Y and Z direction (3 subsets)
* chunks: Each vibration-direction is split into chunks of max. 100 000 datapoints
The core of each chunk is a numpy array `values.npy` which is a 1D array that contains the vibration signal.

Note: This data hierarchy treats the vibration signals as univariate time series.
As you can see in the example above, if there are multiple channels, it is best to create a subset for each channel.

### Data Ingestion Pipeline
Since each dataset comes in its own format, Vibrana employs a three-stage pipeline to ingest the data into the system. Each dataset is therefore stored in three stages:
1. Raw: The dataset is stored on the disk as it was received, for instance as CSV file or parquet file.
2. Parsed: Since the datasets are so individual, a unique parser is written per dataset. This parser transforms the dataset to a vibrana-specific intermediate representation, which results in the following directory structure for each dataset:
```
[dataset]
--> [subset]
    --> values*.npy
```
This means, that each dataset is parsed to 1D Numpy arrays that contain the vibration signals.
The numpy arrays need to start with "values" and anything after "values" is treated as the chunk prefix when naming the chunks.

However, even the parsed folder is not uniform regarding the structure, since the only requirement is a list of "values*.npy" files, but they can be arbitrarily nested in folders.
3. Chunks: To resolve the aforementioned issue, the data is now processed again. The chunk-script is essentially a crawler that recursively processes all "values*.npy" arrays. The array is loaded and split into chunks of 100 000 values.
For each chunk, several plots are precomputed, together with the time delay embedding.

Note: DXD Files are treated a bit differently since they also have timestamps and event markers. In this case the requirement is that these are grouped together in folders during the parsed stage.

The example below illustrates the process based on vibration signals collected in a hydro power plant:
1. Raw:
```
hydro #dataset
--> vibrationsdaten_Nov4-5_2022.parquet
```
The vibration signals are stored in a parquet file where each column is a vibration direction.

2. Parsed:
```
hydro #dataset
--> hydro-1 #subset
    --> values-hydro-1-x.npy
    --> values-hydro-1-y.npy
    --> values-hydro-1-z.npy
```

3. Chunks

```
hydro
--> hydro-1-x
    --> hydro-1-x-0000
            events.npy
            freq.npy
            meta.json
            preview.png
            preview_projected.png
            projected.npy
            spectro.png
            timestamps.npy
            values.npy
    --> hydro-1-x-0001
            events.npy
            freq.npy
            meta.json
            preview.png
            preview_projected.png
            projected.npy
            spectro.png
            timestamps.npy
            values.npy
     ...
```

### Available Parsers and Datasets
All parsers are located in the "parser" directory.

#### Hydro
Vibrations measured on the inside of a hydro power plant. The three subsets show a small window of a small accident, which occurred during maintenance operations.

Parser: `hydro.py`
The parser takes a small slice of the hydro vibrations and stores all three directions in separate value.npy files.

#### Binder
This dataset features measurements acquired from a sorting machine that sorts cobbles by their size. To achieve this, a sieve is utilized, that naturally wears out, causing larger cobbles to fall through. The goal is to measure the impact of cobbles on a metal plate beneath the sieve. The dataset shows vibrations of the metal plate, with and without anomalies.

Parser: `binder.py`
Each subset contains two dxd files: One dxd file with and the other without anomalies.
Note that the parser for binder already does the chunking at the end.

#### Gravitational Waves
Synthetic dataset highlighting hidden patterns in noise. The parser acts as a generator for data where the "raw data" is a sample of a signal that will be embedded in noise.

Parser: `grav_waves.py`

#### Engine Run To Failure
Vibrations acquired from the bearing of an engine in a run-to-failure setting. 

Parser: `nasa-bearings.py`

#### Engine Multiple Runs
Vibrations acquired from an engine, showing multiple runs (with and without damage). The subsets highlight the difference if noise is applied.

Parser: `motor.py`


### Chunking

All the above-mentioned parsers, except binder (historic relict I guess, but no worries, can be altered accordingly),  produce 1D numpy arrays in the parsed stage.
The script `extract_chunks.py` processes an entire dataset, thus iterating each subset and extracting the chunks accordingly.
