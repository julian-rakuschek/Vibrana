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
    Radius, Frequency, Distance, Age, Uncertainty
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
    subsets: { [subset: string]: { file: string; name: string } };
    description?: string;
    task?: string;
    source?: string;
    loader: string;
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
        tde: Histogram;
        psd: { f: number[]; Pxx_spec: number[] };
    };
    label: {
        tde: number;
        psd: number;
    };
}

export type ProvenanceSeed = {
    index: number;
    label: number;
}

export type Provenance = {
    dataset: string;
    subset: string;
    coverage: number;
    signal_length: number;
    breakpoints: {
        tde: ProvenanceSeed[];
        psd: ProvenanceSeed[];
    }
}

export type ClusterColorMapping = {
    [key: number]: string;
}

export type Delta = {
    index: number;
    new_label: number;
}

export type ClusterDelta = {
    tde: number[];
    psd: number[];
}

export type ParameterSettings = {
    tde: {
        eps: number;
        minPoints: number;
        sliding_window_size: number;
    };
    psd: {
        eps: number;
        minPoints: number;
    };
    sampling: {
        samplingAlgorithm: string;
        intervals: number[][];
        running: boolean;
        slice_size: number;
    };
}

export type ParameterSettingsUpdate = {
    tde?: {
        eps?: number;
        minPoints?: number;
        sliding_window_size?: number;
    };
    psd?: {
        eps?: number;
        minPoints?: number;
    };
    sampling?: {
        slice_size?: number;
        samplingAlgorithm?: string;
        intervals?: number[][];
        running?: boolean;
    };
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