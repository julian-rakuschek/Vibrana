<script lang="ts">

    import Navbar from "@components/manage/Navbar.svelte";
</script>

<Navbar isBeige/>
<div class="w-full h-full bg-[#faf9f5]">
    <div class="w-full md:w-1/2 mx-auto">
        <p class="text-2xl">Development Demos</p>
        <p class="italic">These are some playground demos with dummy data for sub-components in Vibrana, for example to
            demonstrate the working of incremental clustering. They are mainly used during development to test
            individual components.</p>
        <div class="flex flex-col items-center md:flex-row pt-8 gap-5 flex-wrap">
            <a href="/demos/brushing">
                <div class="w-80 h-52 bg-indigo-800 rounded-lg flex flex-col items-center p-5 text-white cursor-default transition hover:-translate-y-5 shadow-slate-400 shadow-lg hover:shadow-slate-500">
                    <img src="/demos/brushing.gif" alt="Preview" class="w-full h-full object-contain"/>
                    <p class="font-semibold mt-1">Brushing</p>
                </div>
            </a>
            <a href="/demos/cluster">
                <div class="w-80 h-52 bg-indigo-800 rounded-lg flex flex-col items-center p-5 text-white cursor-default transition hover:-translate-y-5 shadow-slate-400 shadow-lg hover:shadow-slate-500">
                    <img src="/demos/clustering.gif" alt="Preview" class="w-full h-full object-contain"/>
                    <p class="font-semibold mt-1">Incremental Clustering</p>
                </div>
            </a>
        </div>
    </div>
</div>


