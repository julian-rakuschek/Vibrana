import {DefaultPageWithBoundaries} from "components/organisms/DefaultPage";
import {ReactElement} from "react";
import {Link, useParams} from "react-router-dom";
import ThreeChartsWrapper from "components/organisms/ThreeChartsWrapper";
import {ArrowLeftIcon} from "@heroicons/react/24/solid";

export default function AnalyzeSamplePage(): ReactElement {
    const {machineID, sampleID} = useParams();

    return (
        <DefaultPageWithBoundaries menuDarkMode>
            {machineID && sampleID &&
                <ThreeChartsWrapper machineId={machineID} sampleId={sampleID} />
            }
            <Link className="fixed top-3 left-3 bg-white rounded-full shadow-lg p-3 flex justify-center items-center transition hover:shadow-xl" to={`/machines/${machineID}/analyze`}>
                <ArrowLeftIcon className="w-5 h-5" />
            </Link>
        </DefaultPageWithBoundaries>
    );
}