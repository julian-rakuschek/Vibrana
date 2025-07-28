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

export type DatasetConfig = {
    name: string;
    folder: string;
    description: string;
    task: string;
    source: string;
    chunks_or_stream_or_large: "chunks" | "stream" | "large";
    in_memory: boolean;
    subsets: { [subset: string]: SubsetConfig };
}

export type SubsetConfig = {
    name: string;
    file: string;
    slice_size: number;
    sliding_window_size: number;
}

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
    feature_descriptors: {
        radii_distribution: Histogram;
        freq_distribution: Histogram;
    }
}

export type DistributionControlPoints = { x: number; y: number; active: boolean; index: number }

export type DistributionWeights = {
    controlPoints: DistributionControlPoints[];
    curve: Point[];
}

export type ParameterSettings = {
    eps: number;
    minPoints: number;
    samplingAlgorithm: string;
    threads: number;
    maxThreads: number;
    weights: DistributionWeights;
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