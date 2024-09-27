import {ReactElement} from "react";
import NewChart from "components/organisms/NewChart";
import {useParams} from "react-router-dom";
import {ColorMode, ProjectionMode, WindowMode} from "../../../../../types";

export default function NewChartsPage(): ReactElement {
     const {machineID, sampleID} = useParams();

    return <>{machineID && sampleID &&  <NewChart sampleId={sampleID} machineId={machineID} settings={{color: ColorMode.Radius, window: WindowMode.Sliding, window_size: 1000, projection: ProjectionMode.Paths}} />}</>
}