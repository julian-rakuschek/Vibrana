export type ErrorResponse = { success: false; message: string; details?: string[] };
export type AppResponse<T> = { success: true } & T | ErrorResponse;
export type DefaultAppResponse = AppResponse<unknown>;
export type ListAppResponse<T> = AppResponse<{ rows: T[] }>;

export type Diff<T, U> = T extends U ? never : T;
export type Successful<T> = Diff<T, { success: false }>;
export type Failed<T> = Diff<T, { success: true }>;

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

export enum ProjectionMode {
    Paths, Cluster
}

export type ThreeChartsSettingsType = {
    window: WindowMode;
    window_size: number;
    color: ColorMode;
    projection: ProjectionMode;
}



export type Annotation = {
    from: number;
    to: number;
    color?: string | number;
}

export type Point = {
    x: number;
    y: number;
}

export type DataPoint = {
    x: number;
    y: number;
    meta_value: number;
}

export type Dataset = DataPoint[];

export type Earcut = {
    vertices: number[],
    hole_indices: number[]
}

export type TimeSeriesPoint = {
    x: number;
    y: number;
}

export type ProjectedPoint = {
    timeSeriesIndex: number;
    projectedIndex: number;
    coords: number[]
};