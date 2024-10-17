<script lang="ts">
    import {Dialog, DialogOverlay, Transition, TransitionChild} from "@rgossiaux/svelte-headlessui";
    import Dropzone from "svelte-file-dropzone";
    import {type FileWithPath} from "file-selector";
    import axios from "axios";
    import type {ParseStatus} from "@lib/types";
    import {ApiRoutes} from "@lib/api/ApiRoutes";


    function handleFilesSelect(e) {
        const {acceptedFiles, fileRejections} = e.detail;
        if (acceptedFiles.length > 0) {
            selected_file = acceptedFiles[0]
        }
    }

    export let isOpen = false;
    export let machine: string;

    let prefix = ""
    let sampleSize = 100000
    let saveParsed = false;
    let progress: number | null = null;
    let selected_file: FileWithPath | undefined;
    let parseStatus: ParseStatus | null = null;
    let statusUpdateInterval: ReturnType<typeof setInterval>;
    let uploadFinished = false;

    const updateParseStatus = async (filename: string) => {
        parseStatus = await ApiRoutes.getUploadStatus.fetch({params: {machineId: machine, filename: filename}})
    }


    const upload = () => {
        if (selected_file === undefined || sampleSize === null) return;
        progress = 0;
        parseStatus = null;
        uploadFinished = false;
        statusUpdateInterval = setInterval(() => updateParseStatus(selected_file?.name), 500)
        const formData = new FormData();
        formData.append("file", selected_file);
        formData.append("prefix", prefix);
        formData.append("maxSampleSize", sampleSize.toString());
        formData.append("saveParsed", saveParsed ? "true" : "false");
        axios.post(`/api/db/${machine}/upload`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            },
            onUploadProgress: progressEvent => progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        }).then(() => {
            updateParseStatus(selected_file?.name)
            prefix = ""
            progress = 100;
            selected_file = undefined;
            uploadFinished = true;
            clearInterval(statusUpdateInterval)
        }).catch(err => console.log(err))
    }
</script>

<Transition show={isOpen}>
    <Dialog open={isOpen} on:close={() => (isOpen = false)} class="z-50 fixed top-0 left-0 flex justify-center items-center w-full h-full">
        <TransitionChild
                enter="ease-out duration-300"
                enterFrom="opacity-0"
                enterTo="opacity-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100"
                leaveTo="opacity-0"
        >
            <DialogOverlay class="fixed top-0 left-0 bg-black/30 w-full h-full"/>
        </TransitionChild>
        <div class="z-10">
            <TransitionChild
                    enter="ease-out duration-200"
                    enterFrom="opacity-0 scale-75"
                    enterTo="opacity-100 scale-100"
                    leave="ease-in duration-100"
                    leaveFrom="opacity-100 scale-100"
                    leaveTo="opacity-0 scale-100"
            >
                <div class="bg-white rounded-lg p-4 flex flex-col items-center gap-4 min-w-[300px]">
                    <p class="text-lg font-semibold">Upload Sample</p>
                    <div class="relative w-full">
                        <label for="name" class="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900">Prefix</label>
                        <input type="text" autocomplete="off" name="name" id="name" bind:value={prefix}
                               class="block w-full rounded-md border-0 py-1.5 px-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 placeholder:leading-6 focus:ring-1 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                               placeholder="Prefix for Samples">
                    </div>
                    <div class="relative w-full">
                        <label for="name" class="absolute -top-2 left-2 inline-block bg-white px-1 text-xs font-medium text-gray-900">Maximum Sample Size</label>
                        <input type="number" autocomplete="off" name="name" id="name" bind:value={sampleSize}
                               class="block w-full rounded-md border-0 py-1.5 px-2 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 placeholder:leading-6 focus:ring-1 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                               placeholder="Sample Size">
                    </div>
                    <div class="relative w-full flex items-start">
                        <div class="flex h-6 items-center">
                            <input bind:value={saveParsed} id="save-parsed" aria-describedby="save-parsed-description" name="save-parsed" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600">
                        </div>
                        <div class="ml-3 text-sm leading-6">
                            <label for="save-parsed" class="font-medium text-gray-900">Save full-length parsed signal additionally on disk</label>
                            <p id="save-parsed-description" class="text-gray-500">If enabled, a complete numpy array of full input length will be saved on the disk. This is useful for experiments on the entire signal.</p>
                        </div>
                    </div>
                    <Dropzone on:drop={handleFilesSelect} multiple={false}/>
                    {#if selected_file}
                        <p>{selected_file.name}</p>
                    {/if}
                    <button on:click={upload} class="rounded-md bg-indigo-50 px-2.5 py-1.5 text-sm font-semibold text-indigo-600 shadow-sm hover:bg-indigo-100">Upload</button>
                    {#if progress}
                        <div class="w-full bg-gray-200 rounded-full h-2.5">
                            <div class="bg-indigo-600 h-2.5 rounded-full" style={`width: ${progress}%`}></div>
                        </div>
                    {/if}
                    {#if parseStatus}
                        <div class="bg-gray-100 rounded-lg p-4 w-2/3">
                            {#if parseStatus.dwparse}
                                <p>DWParse: {parseStatus.dwparse.status}</p>
                            {/if}
                            {#if parseStatus.split}
                                <p>Splitting: {parseStatus.split.status}</p>
                                {#each Object.entries(parseStatus.split.items) as [key, value]}
                                    <p class={`${value === "done" ? "text-green-500" : "text-gray-800"}`}>{key}: {value}</p>
                                {/each}
                            {/if}
                        </div>
                    {/if}
                    {#if uploadFinished}
                        <p class="text-center text-green-500">Upload finished!</p>
                    {/if}
                </div>
            </TransitionChild>
        </div>
    </Dialog>
</Transition>