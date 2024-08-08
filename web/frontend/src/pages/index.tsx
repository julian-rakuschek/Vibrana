import { DefaultPageWithBoundaries } from "components/organisms/DefaultPage";
import {ReactElement} from "react";

export default function Home(): ReactElement {

  return (
    <DefaultPageWithBoundaries showHeader>
        <div className="grow flex flex-col items-center justify-center">
            <img width={400} alt="" src="/vibrava.png"></img>
            <p className="text-[#1c2934] text-6xl font-bold">Vibrava</p>
            <p className="text-[#1c2934] text-xl">Analyze and Annotate Vibration Signals Easily</p>
        </div>
    </DefaultPageWithBoundaries>
  );
}