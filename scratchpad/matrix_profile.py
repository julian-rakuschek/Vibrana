import math
import os.path
from pathlib import Path

import numpy as np
import stumpy
from matplotlib import pyplot as plt


def compute_matrix_profile(values, m):
    return stumpy.gpu_stump(values, m)


def process_folder(folder):
    print(f"Computing matrix profile of {folder}")
    base_path = os.path.join(Path(__file__).parents[1], "data", folder)
    values = np.load(os.path.join(base_path, "values.npy"))
    mat = compute_matrix_profile(values, 2000)
    np.save(os.path.join(base_path, "matrix.npy"), mat)
    plt.clf()
    plt.plot(mat[:, 0])
    plt.savefig(os.path.join(base_path, "matrix.png"))


def process_array(values, save_folder):
    print(f"Computing matrix profile of {save_folder}")
    base_path = os.path.join(Path(__file__).parents[1], "data", save_folder)
    mat = compute_matrix_profile(values, 2000)
    np.save(os.path.join(base_path, "matrix_combined.npy"), mat)
    plt.clf()
    plt.plot(mat[:, 0])
    plt.savefig(os.path.join(base_path, "matrix_combined.png"))


def compute_all():
    process_folder("5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde")
    process_folder("5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde 10-16 gemischt")
    process_folder("16-31 Korngröse 5 cm, 45 Grad Aus Förderrinne 2t pro Stunde")
    process_folder("16-31 Korngröse 5 cm, 45 Grad Aus Förderrinne 2t pro Stunde gemischt 31,5-62")
    process_folder("Metall platte, FEDER Montiert, 10-16 Korngröse, 25 cm fall, sensor fest xx t pro stunde gemischt round 2")
    process_folder("Metall platte, FEDER Montiert, 10-16 Korngröse, 25 cm fall, sensor fest xx t pro stunde round 2")

def compute_all_fluss():
    fluss_preprocess("5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde", "5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde 10-16 gemischt")
    fluss_preprocess("16-31 Korngröse 5 cm, 45 Grad Aus Förderrinne 2t pro Stunde", "16-31 Korngröse 5 cm, 45 Grad Aus Förderrinne 2t pro Stunde gemischt 31,5-62")
    fluss_preprocess("Metall platte, FEDER Montiert, 10-16 Korngröse, 25 cm fall, sensor fest xx t pro stunde gemischt round 2", "Metall platte, FEDER Montiert, 10-16 Korngröse, 25 cm fall, sensor fest xx t pro stunde round 2")



def fluss_preprocess(folder1, folder2, return_array=False):
    base_path_1 = os.path.join(Path(__file__).parents[1], "data", folder1)
    base_path_2 = os.path.join(Path(__file__).parents[1], "data", folder2)

    values_1 = np.load(os.path.join(base_path_1, "values.npy"))
    values_1 = values_1[math.floor(len(values_1) * 0.2):math.floor(len(values_1) * 0.8)]
    values_2 = np.load(os.path.join(base_path_2, "values.npy"))
    values_2 = values_2[math.floor(len(values_2) * 0.2):math.floor(len(values_2) * 0.8)]
    print(len(values_1))
    print(len(values_2))

    values = np.concatenate([values_1, values_2], axis=0)
    if return_array:
        return values
    process_array(values, folder1)


def fluss_apply(folder1, folder2):
    base_path = os.path.join(Path(__file__).parents[1], "data", folder1)
    mat = np.load(os.path.join(base_path, "matrix_combined.npy"), allow_pickle=True)
    values = fluss_preprocess(folder1, folder2, return_array=True)
    return
    cac, regime_locs = stumpy.fluss(mat[:, 1], 2000, 2)
    plt.clf()
    plt.plot(values)
    plt.axvline(regime_locs[0], color="red")
    plt.savefig(os.path.join(base_path, "matrix_segment.png"))
    print(regime_locs)


def compute_test():
    random_values = np.random.rand(1000)
    mat = compute_matrix_profile(random_values, 100)
    print(mat)




if __name__ == '__main__':
    # compute_all_fluss()
    fluss_apply("5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde", "5-10 Korngröse 5 cm, 45 Grad Aus Förderrinne 1t pro Stunde 10-16 gemischt")
    fluss_apply("16-31 Korngröse 5 cm, 45 Grad Aus Förderrinne 2t pro Stunde", "16-31 Korngröse 5 cm, 45 Grad Aus Förderrinne 2t pro Stunde gemischt 31,5-62")
    fluss_apply("Metall platte, FEDER Montiert, 10-16 Korngröse, 25 cm fall, sensor fest xx t pro stunde gemischt round 2", "Metall platte, FEDER Montiert, 10-16 Korngröse, 25 cm fall, sensor fest xx t pro stunde round 2")
