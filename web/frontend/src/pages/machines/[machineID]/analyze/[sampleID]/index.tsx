import {DefaultPageWithBoundaries} from "components/organisms/DefaultPage";
import {ReactElement, useState} from "react";
import {Link, useParams} from "react-router-dom";
import ThreeChartsWrapper from "components/organisms/ThreeChartsWrapper";
import {ArrowLeftIcon} from "@heroicons/react/24/solid";
import ThreeChartsSettings from "components/molecules/ThreeChartsSettings";
import {ColorMode, ProjectionMode, ThreeChartsSettingsType, WindowMode} from "../../../../../types";

export default function AnalyzeSamplePage(): ReactElement {
    const {machineID, sampleID} = useParams();
    const [settings, setSettings] = useState<ThreeChartsSettingsType>({window: WindowMode.Sliding, color: ColorMode.Radius, projection: ProjectionMode.Paths})

    return (
        <DefaultPageWithBoundaries menuDarkMode>
            {machineID && sampleID &&
                <ThreeChartsWrapper machineId={machineID} sampleId={sampleID} settings={settings} />
            }
            <Link className="fixed top-3 left-3 bg-white rounded-full shadow-lg p-3 flex justify-center items-center transition hover:shadow-xl" to={`/machines/${machineID}/analyze`}>
                <ArrowLeftIcon className="w-5 h-5" />
            </Link>
            <div className="fixed top-3 right-3">
               <ThreeChartsSettings settings={settings} setSettings={setSettings} />
            </div>
        </DefaultPageWithBoundaries>
    );
}