export type ErrorResponse = { success: false; message: string; details?: string[] };
export type AppResponse<T> = { success: true } & T | ErrorResponse;
export type DefaultAppResponse = AppResponse<unknown>;
export type ListAppResponse<T> = AppResponse<{ rows: T[] }>;

export type Diff<T, U> = T extends U ? never : T;
export type Successful<T> = Diff<T, { success: false }>;
export type Failed<T> = Diff<T, { success: true }>;


export type Dataset = {
    name: string;
    folder: string;
    description: string;
    tasks: string[];
    subsets: { name: string; folder: string }[]
}

export type ObjectId = {
  $oid: string;
};

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
    Radius, Frequency, Distance
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

export type AnomalyMetric = {
    ratio: number,
    count: number,
    distances_reduced: number[],
    dataset: string,
    subset: string
    chunk: string
}

export type ParseStatus = {
    dwparse?: {
        status: string
    };
    split?: {
        status: string;
        items: {[file: string]: string}
    };
}

export type AnalysisPostData = {
    normals: { dataset: string, subset: string, chunks: string[] },
    labels: Label[]
}

export type LabelCount = {
    _id: string;
    count: number;
}