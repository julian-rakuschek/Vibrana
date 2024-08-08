import {ReactElement} from "react";
import {useSamples} from "lib/hooks";
import {Link} from "react-router-dom";

export default function SamplesList({machine}: { machine: string }): ReactElement {
    const samples = useSamples(machine);

    return <div className="flex flex-row flex-wrap gap-6 p-4 justify-center">
        {samples.map(s =>
            <Link to={`/machines/${machine}/analyze/${s}`} className="flex flex-col justify-center items-center w-[400px] h-[150px] shadow-lg rounded-lg px-2 transition hover:shadow-xl">
                <img src={`/api/db/${machine}/samples/${s}/thumbnail`} alt="thumbnail"/>
                <span className="mb-4">{s}</span>
            </Link>)}
    </div>
}