export type ErrorResponse = { success: false; message: string; details?: string[] };
export type AppResponse<T> = { success: true } & T | ErrorResponse;
export type DefaultAppResponse = AppResponse<unknown>;
export type ListAppResponse<T> = AppResponse<{ rows: T[] }>;

export type Diff<T, U> = T extends U ? never : T;
export type Successful<T> = Diff<T, { success: false }>;
export type Failed<T> = Diff<T, { success: true }>;

export type Example = {
    a: string;
    b: number
}

export enum ToastType {
  Info = "Info",
  Success = "Success",
  Warning = "Warning",
  Error = "Error",
}

export enum ColorMode {
    Radius, Frequency, Distance
}

export type ToastDto = {
  type: ToastType;
  message: string;
};

export type Annotation = {
    from: number;
    to: number;
    color: string;
}

export type DataPoint = {
    x: number;
    y: number;
    meta_value: number;
}

export type Dataset = DataPoint[];