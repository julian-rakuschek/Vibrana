<script lang="ts">

import {DBSCAN_VibrationFingerprints} from "@lib/algorithms/incrementalDBSCAN";

const data = [
    {
        index: 0,
        feature_descriptors: {
            radii_distribution: {
                counts: [1, 0, 0]
            }
        }
    },
    {
        index: 1,
        feature_descriptors: {
            radii_distribution: {
                counts: [0, 1, 0]
            }
        }
    },
    {
        index: 2,
        feature_descriptors: {
            radii_distribution: {
                counts: [0, 0, 1]
            }
        }
    }
]

const to_insert = {
        index: 3,
        feature_descriptors: {
            radii_distribution: {
                counts: [0, 0, 0.9]
            }
        }
    }

const dbscan = new DBSCAN_VibrationFingerprints(0.5, 3, data);
dbscan.insert(to_insert)
const res = dbscan.neighborhoodQuery(data[2]);
console.log(res);
</script>

