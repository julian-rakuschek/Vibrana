import {ReactElement} from "react";
import {useMachines} from "lib/hooks";
import {Link} from "react-router-dom";

export default function MachinesList(): ReactElement {
    const machines = useMachines()

    return <div className="flex flex-row p-10">
        {machines.map(m =>
            <Link
                to={`/machines/${m}/analyze`}
                className="w-[300px] h-[40px] shadow-lg rounded-lg flex flex-row justify-around items-center transition hover:shadow-xl"
            >
                <span className="font-semibold">{m}</span>
                <div className="rounded-full w-[15px] h-[15px] bg-green-500"></div>
            </Link>
        )}
    </div>
}