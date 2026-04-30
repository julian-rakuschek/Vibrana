export type ErrorResponse = { success: false; message: string; details?: string[] };
export type AppResponse<T> = { success: true } & T | ErrorResponse;
export type DefaultAppResponse = AppResponse<unknown>;

export enum ColorMode {
    Radius, Frequency, Distance, Age, Uncertainty
}

export enum IntervalModes { ADD, DELETE }


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

export type Histogram = {
    bins: number[];
    counts: number[];
}

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

export type AveragePsdSegment = {
    label: number;
    averagePsd: number[];
}

export type TimeInformation = {
    start_time: string;
    end_time: string;
    total_sample_points: number;
    display_as_delta: boolean;
}


export type ClusterColorMapping = {
    [key: number]: string;
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

export type Point = {
    x: number;
    y: number;
}
