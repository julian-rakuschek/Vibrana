import copy

from pymongo.synchronous.database import Database

from vibrana.backend.helper import database

artificial_fps = [
    {"start_index": 1, "slice_length": 3},
    {"start_index": 2, "slice_length": 3},
    {"start_index": 7, "slice_length": 1},
    {"start_index": 10, "slice_length": 2},
    {"start_index": 10, "slice_length": 2},
    {"start_index": 13, "slice_length": 2},
    {"start_index": 14, "slice_length": 2},
]

def get_coverage(db: Database, dataset: str, subset: str):
    fps = db["fingerprints"].find({"dataset": dataset, "subset": subset}, {"start_index": 1, "slice_length": 1, "label": 1, "max_index": 1}).sort("start_index")
    current_fp = None
    covered_data_points = 0
    for fp in fps:
        fp['end_index'] = fp['start_index'] + fp['slice_length'] - 1
        if current_fp is None:
            current_fp = copy.deepcopy(fp)
            continue
        if fp["start_index"] <= current_fp["end_index"]:
            current_fp["slice_length"] = fp["end_index"] - current_fp["start_index"] + 1
        else:
            covered_data_points += current_fp["slice_length"]
            current_fp = copy.deepcopy(fp)
    covered_data_points += current_fp["slice_length"]
    signal_length = current_fp["max_index"] + 1
    return covered_data_points, signal_length

def get_breakpoints(db: Database, dataset: str, subset: str, feature: str):
    def repr(fp):
        return {"index": fp["start_index"], "label": fp["label"][feature]}

    fps = db["fingerprints"].find({"dataset": dataset, "subset": subset}, {"start_index": 1, "slice_length": 1, "label": 1, "max_index": 1}).sort("start_index")
    current_fp = None
    breakpoints = []
    for fp in fps:
        if current_fp is None:
            current_fp = copy.deepcopy(fp)
            continue
        if fp["label"][feature] != current_fp["label"][feature]:
            breakpoints.append(repr(current_fp))
            breakpoints.append(repr(fp))
        current_fp = copy.deepcopy(fp)
    if not breakpoints and current_fp:
        breakpoints.append(repr(current_fp))
        breakpoints.append(repr(current_fp))
    return breakpoints

if __name__ == '__main__':
    res = get_breakpoints("tde")