import { DefaultPageWithBoundaries } from "components/organisms/DefaultPage";

export default function Home(): JSX.Element {

  return (
    <DefaultPageWithBoundaries menuDarkMode>
        <div className="landing-page-gradient grow flex flex-col items-center justify-center">
            <p className="text-white text-8xl font-bold">Empty Project</p>
            <p className="text-white text-xl">Have fun</p>
        </div>

    </DefaultPageWithBoundaries>
  );
}