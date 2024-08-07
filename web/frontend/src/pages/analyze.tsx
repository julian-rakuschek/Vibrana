import {DefaultPageWithBoundaries} from "components/organisms/DefaultPage";
import {useDummyValues, useDummyProjected, useLabels} from "lib/hooks";
import ThreeCharts from "components/organisms/ThreeCharts";

export default function AnalyzePage(): JSX.Element {
    const values = useDummyValues();
    const projected = useDummyProjected();
    const labels = useLabels("dummy");

    return (
        <DefaultPageWithBoundaries menuDarkMode>
            {values.length > 0 && projected.length > 0 &&
                <ThreeCharts series={"dummy"} labels={labels} timeseries={values} projected={projected} height={"100%"} width={"100%"}/>
            }
        </DefaultPageWithBoundaries>
    );
}