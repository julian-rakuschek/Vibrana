<script lang="ts">
    import {getContext} from "svelte";
    import StyledDisclosure from "@components/atoms/StyledDisclosure.svelte";

    const {ro} = getContext("ro") as { ro: boolean }

    let tab_paths = "no_anomaly"
</script>

<div class="w-full">
    <p class="text-2xl font-semibold mb-1">What is Vibrana?</p>
    <p>
        Vibrana is a tool for analyzing vibration signals from a different perspective.
        Usually one would apply standard techniques from signal processing, however, these methods are often
        incomprehensible for non-experts.
        We aim to address this issue by implementing an exploration workflow using time-delay embeddings.
        The idea is simple: Take a sliding window view of the signal and apply dimensionality reduction, this means that
        each window is interpreted as a point in high dimensions and subsequently projected into the 2D plane.
        The result is a mapping of each point in the signal to another point in a 2D point cloud.
        An example of such a mapping from the signal to the projection is shown in the animation below:
    </p>
    <div class="w-full flex justify-center">
        <video src="/intro/videos/mapping-animation.mp4" autoplay loop muted></video>
    </div>

    <p>
        The projection offers valuable insights, because anomalies in the signal will cause well-structured patterns in
        the cloud.
        The example below shows two signals: The left signal has no anomalies and therefore only yields a chaotic cloud,
        however, the signal on the right-hand side contains anomalies.
        This results in several patterns in the projection, especially in the outer rings.
    </p>
    <div class="flex flex-row my-5">
        <img src="/intro/images/binder-1.png" class="w-1/2"/>
        <img src="/intro/images/binder-2.png" class="w-1/2"/>
    </div>
    <p>
        This time delay embedding is at the heart of Vibrana: It offers a visual indicator if the signal is behaving in
        an unexpected way.
    </p>
    <p class="mb-5">The Vibrana tool offers the following features:</p>
    <ul class="list-disc list-inside ml-5">
        <li>Exploration of vibration signals through time-delay embeddings.</li>
        <li>Annotating windows in the signal.</li>
        <li>Similarity search with the assigned labels to quickly classify signals (anomalous vs normal).</li>
    </ul>
    <p class="text-2xl font-semibold mt-10 mb-1">How to analyze data with Vibrana</p>
    <p>
        The first step is to upload the signals.
        We assume that our target group wants to analyze vibrations caused by machines, which is why groups of signals
        are called <i>machines</i>.
        Currently, only <i>dxd</i> files are supported, which are highly compressed signals collected and analyzed by <a
            href="https://dewesoft.com/de" class="text-indigo-500">DEWESoft</a> products.
    </p>
    {#if ro}
        <div class="my-5 bg-red-100 text-red-500 rounded-lg p-3"><b>Note:</b>
            This demo is in read-only mode, therefore the upload feature is disabled.
        </div>
    {/if}
    <p>
        During upload, the signal is split into smaller chunks to be more manageable by the visualization.
        After the upload is finished, the user may start exploring the chunks of the signal through the three-charts
        view:
    </p>
    <div class="flex flex-col justify-center items-center relative my-5">
        <img src="/intro/images/vibrana-overview.png"/>
        <div class="absolute top-0 right-0 bg-[#304ffe] text-white rounded-lg p-1 text-sm px-3 text-center">
            <span class="bg-white text-indigo-700 rounded-full px-2 mr-3">1</span> Select a subset
        </div>
        <div class="absolute top-[25%] right-0 bg-[#304ffe] text-white rounded-lg p-1 text-sm px-3 text-center">
            <span class="bg-white text-indigo-700 rounded-full px-2 mr-3">2</span> Assign labels
        </div>
        <div class="absolute top-[60%] right-0 bg-[#304ffe] text-white rounded-lg p-1 text-sm px-3 text-center">
            <span class="bg-white text-indigo-700 rounded-full px-2 mr-3">3</span> Explore 2D projection
        </div>
    </div>
    <p>
        First, the color in all three charts corresponds to the radius in the point cloud.
        Therefore, red means the point is far outside while blue points are located near the center.
        Note that this visual mapping is designed to guide users towards points of interest within the signal,
        therefore chart 1 is used in order to zoom in, while chart 2 then presents the selected subset.
    </p>
    <div class="my-5 bg-indigo-50 text-indigo-500 rounded-lg p-3"><b>Hint:</b>
        Many interesting anomalies tend to accumulate towards the outer rings of the projection, therefore it is
        advisable to examine those regions first.
    </div>
    <p>
        In order to validate an anomaly, the path tracing tool can be used.
        When the time series is projected into the 2D plane, the patterns tend to form traces.
        It can be observed, that anomalies lead to well structured rings while noise results in chaotic paths.
        The following two tabs show both cases where the path tool is used.
    </p>
    <div class="flex flex-row w-full justify-center gap-5 mt-5">
        <button on:click={() => tab_paths = "no_anomaly"}
                class={`${tab_paths === "no_anomaly" ? "border-indigo-500" : "border-transparent"} border-2 rounded-md bg-indigo-50 px-2.5 py-1.5 text-sm font-semibold text-indigo-600 shadow-sm hover:bg-indigo-100`}>
            Normal Signal
        </button>
        <button on:click={() => tab_paths = "anomaly"}
                class={`${tab_paths === "anomaly" ? "border-indigo-500" : "border-transparent"} border-2 rounded-md bg-indigo-50 px-2.5 py-1.5 text-sm font-semibold text-indigo-600 shadow-sm hover:bg-indigo-100`}>
            Anomalous Signal
        </button>
    </div>
    {#if tab_paths === "no_anomaly"}
        <div class="w-full flex justify-center">
            <video src="/intro/videos/paths-no-anomaly.mp4" autoplay loop muted></video>
        </div>
    {/if}
    {#if tab_paths === "anomaly"}
        <div class="w-full flex justify-center">
            <video src="/intro/videos/paths-anomaly.mp4" autoplay loop muted></video>
        </div>
    {/if}
    <div class="my-5 bg-red-100 text-red-500 rounded-lg p-3"><b>Note:</b>
        This assumes that the background of the signal is noise while anomalies exhibit strong frequency patterns.
        Other datasets may result in different point clouds, but the path tracing tool is still a valid exploration
        tool.
    </div>

    <p>
        As soon as valid anomalies have been discovered, they can be saved as labels using chart 2.
        The labels are used in the next step to classify the signals (normal vs anomalous) using similarity search.
        That is, the saved anomaly is slided across all signals and in each timestep, the similarity is computed using the euclidean distance.
        Therefore, a high similarity of the signal to the label or a low distance from the euclidean distance (beware of the duality) indicates that the pattern occurred again.
    </p>
    <p class="mt-1">
        However, for this to be interpretable, we need a notion of what a normal signal looks like.
        This is achieved by selecting a signal without anomalies in the overview (see the following video).
        As soon as a normal sample and labels are available, the anomaly score can be computed for each signal.
    </p>

    <StyledDisclosure header_text="Video: Selecting Normals" >
        Hi mum
    </StyledDisclosure>

    <div class="w-full h-[500px]"></div>
</div>