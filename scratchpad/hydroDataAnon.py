import polars as pl
from hashlib import sha256


def process_large_csv(input_file, output_file, columns_to_remove):
    """
    Process a large CSV file using Polars:
    1. Read the CSV file
    2. Remove specified columns
    3. Anonymize remaining column names
    4. Write to a new CSV file

    Args:
        input_file (str): Path to the input CSV file
        output_file (str): Path to save the processed CSV file
        columns_to_remove (list): List of column names to remove
    """
    # Read the CSV file in a memory-efficient way using streaming
    df = pl.scan_csv(input_file)

    # Get all column names
    all_columns = df.columns

    # Determine which columns to keep (all except those to be removed)
    columns_to_keep = [col for col in all_columns if col not in columns_to_remove]

    # Select only the columns we want to keep
    df_filtered = df.select(columns_to_keep)

    # Create anonymized column names using SHA-256 hash
    anonymized_columns = {}
    for i, col_name in enumerate(columns_to_keep):
        if col_name == "TimeStamp":
            continue
        hashed = sha256(col_name.encode()).hexdigest()[:8]  # Take first 8 chars of hash
        anonymized_columns[col_name] = f"col_{i}_{hashed}"

    # Rename the columns
    df_renamed = df_filtered.rename(anonymized_columns)

    # Execute the query plan and write to CSV
    df_renamed.sink_csv(output_file)

    print(f"Processing complete. Output saved to {output_file}")
    print(f"Column mapping for reference:")
    for original, anonymized in anonymized_columns.items():
        print(f"  {original} → {anonymized}")


if __name__ == "__main__":
    # Example usage
    input_file = "C:\\Users\\jrakusch\\Datasets\\Hydro\\DataExport_ALL-SENSORS_1Hz.csv"
    output_file = "C:\\Users\\jrakusch\\Datasets\\Hydro\\hydro.csv"

    # Specify the columns to remove by name
    columns_to_remove = ["Vibration.CH1", "Vibration.CH2", "Vibration.CH3", "38_KHI.M2.TRE.LEISTG", "45_KHI.M1.Generator.Messung.Wirkleistung"]

    process_large_csv(input_file, output_file, columns_to_remove)