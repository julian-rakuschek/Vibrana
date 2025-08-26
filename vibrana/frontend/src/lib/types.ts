export type ErrorResponse = { success: false; message: string; details?: string[] };
export type AppResponse<T> = { success: true } & T | ErrorResponse;
export type DefaultAppResponse = AppResponse<unknown>;
export type ListAppResponse<T> = AppResponse<{ rows: T[] }>;

export type Diff<T, U> = T extends U ? never : T;
export type Successful<T> = Diff<T, { success: false }>;
export type Failed<T> = Diff<T, { success: true }>;

// ---------------------------------------------------------
// Enums

export enum ToastType {
  Info = "Info",
  Success = "Success",
  Warning = "Warning",
  Error = "Error",
}

export type ToastDto = {
  type: ToastType;
  message: string;
};

export enum ColorMode {
    Radius, Frequency, Distance, Age
}

export enum WindowMode {
    Disjoint, Sliding
}

export enum SortMode {
    Name, Score
}

export enum ProjectionMode {
    Paths, Cluster
}

// ---------------------------------------------------------
// Data Structures

export type Config = {
    [dataset: string]: DatasetConfig;
}

// Discriminated union of DatasetConfig
export type DatasetConfig =
    | StreamDatasetConfig
    | ChunkDatasetConfig;

export type BaseDatasetConfig = {
    name: string;
    folder: string;
    description?: string;
    task?: string;
    source?: string;
    loader: string;
};

// Stream-specific config
export type StreamDatasetConfig = BaseDatasetConfig & {
    dataset_type: "stream";
    subsets: { [subset: string]: StreamSubsetConfig };
};

// Chunk-specific config
export type ChunkDatasetConfig = BaseDatasetConfig & {
    dataset_type: "chunks";
    subsets: { [subset: string]: ChunkSubsetConfig };
};

export type StreamSubsetConfig = {
    name: string;
    file: string;
};

export type ChunkSubsetConfig = {
    name: string;
    file_list: string[];
};


export type ObjectId = { $oid: string; };

export type Dendrogram = {
  id: string;
  dist?: number;
  left?: Dendrogram;
  right?: Dendrogram;
};

export type ScatterPoint = {
    x: number;
    y: number;
    index: number;
}

export type Histogram = {
    bins: number[];
    counts: number[];
}

export type ClusterHistogram = {
    cluster_id: string;
    color: string;
    size: number;
    relative_size: number;
}[]

export type Fingerprint = {
    index: number;
    slice_length: number;
    start_index: number;
    max_index: number;
    v1: number[];
    v2: number[];
    timestamp: number;
    sliding_window_size: number;
    feature_descriptors: {
        radii_distribution: Histogram;
        freq_distribution: Histogram;
    };
    label: number;
}

export type ClusterColorMapping = {
    [key: number]: string;
}

export type ClusterOverviewSector = {
    indices: number[];
    fingerprintIndices: Set<number>;
    clusterLabel: number | null;
};

export type ClusterDelta = { index: number; new_label: number }[];

export type ParameterSettings = {
    eps: number;
    minPoints: number;
    samplingAlgorithm: string;
    intervals: number[][];
    running: boolean;
}

export type ParameterSettingsUpdate = {
    eps?: number;
    minPoints?: number;
    samplingAlgorithm?: string;
    intervals?: number[][];
    running?: boolean;
}


export type ThreeChartsSettingsType = {
    window: WindowMode;
    windowSize: number;
    color: ColorMode;
    projection: ProjectionMode;
}

export type ChunkListSettingsType = {
    sort: SortMode;
    split: boolean;
}

export type Annotation = {
    from: number;
    to: number;
    color?: string | number;
}

export type LabelBase = Annotation & {
    dataset: string;
    subset: string;
    chunk: string;
}

export type Label = LabelBase & {
    _id: ObjectId;
}

export type Point = {
    x: number;
    y: number;
}

export type Earcut = {
    vertices: number[],
    hole_indices: number[]
}

export type ProjectedPoint = {
    timeSeriesIndex: number;
    projectedIndex: number;
    coords: number[]
};

export type Color = {
    color: string;
    value: number;
}

export type ChartColors = {
    tsColors: Color[];
    projectedColors: Color[];
}




export type SelectedChunk = {
    dataset: string;
    subset: string;
    chunk: string;
}

export type HeatmapTooltip = {
    x: number;
    y: number;
    show: boolean;
    chunk: string;
}