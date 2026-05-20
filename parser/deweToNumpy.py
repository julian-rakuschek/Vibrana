from pathlib import Path

import numpy as np

from parser.lib.dewesoft import dwparser


DXD_FOLDER = Path("/home/jrakusch/Coding/PRESENT/vibrations/vibrana/data/prepared-signals/messfeld/FRE")
OUTPUT_FILE = DXD_FOLDER / "values.npy"


def main():
    files = sorted(DXD_FOLDER.glob("*.dxd"))
    if not files:
        raise FileNotFoundError(f"No .dxd files found in {DXD_FOLDER}")

    lengths = []
    for file in files:
        values, _, _ = dwparser.process_file(str(file))
        lengths.append(len(values))
        del values

    output = np.lib.format.open_memmap(
        OUTPUT_FILE,
        mode="w+",
        dtype=np.float64,
        shape=(sum(lengths),),
    )

    offset = 0
    for file, length in zip(files, lengths):
        values, _, _ = dwparser.process_file(str(file))
        output[offset:offset + length] = values
        output.flush()
        offset += length
        print(f"Wrote {file.name}")

    print(f"Done: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
