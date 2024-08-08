import {ReactElement} from "react";
import {DefaultPageWithBoundaries} from "components/organisms/DefaultPage";
import MachinesList from "components/molecules/MachinesList";

export default function MachinePage(): ReactElement {
    return <DefaultPageWithBoundaries showHeader>
        <MachinesList />
    </DefaultPageWithBoundaries>
}