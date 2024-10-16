<script lang="ts">
    import {Dialog, DialogOverlay, Transition, TransitionChild} from "@rgossiaux/svelte-headlessui";
    import Dropzone from "svelte-file-dropzone";
    import {type FileWithPath} from "file-selector";

    let selected_file: FileWithPath | undefined;

    function handleFilesSelect(e) {
        const {acceptedFiles, fileRejections} = e.detail;
        if (acceptedFiles.length > 0) {
            selected_file = acceptedFiles[0]
        }
    }

    export let isOpen = false;
    let prefix = ""
    let sampleSize = 100000
    let saveParsed = false;

    const upload = () => {

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
                </div>
            </TransitionChild>
        </div>
    </Dialog>
</Transition>