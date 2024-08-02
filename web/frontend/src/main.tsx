import React, {Suspense, useState} from "react";
import ReactDOM from "react-dom/client";
import "./styles/globals.css";
import "./styles/slider.css";
import {QueryClient, QueryClientProvider} from "@tanstack/react-query";
import {createBrowserRouter, Outlet, RouterProvider} from "react-router-dom";
import routes from "~react-pages";
import FourOhFour from "./pages/404";
import {ErrorBoundary} from "react-error-boundary";
import {ErrorPage} from "components/organisms/ErrorPage";
import {FullScreenLoadingSpinner} from "components/atoms/CenteredLoadingSpinner";

(window as any).global = window;

const Root = (): JSX.Element => {

    return (
        <ErrorBoundary FallbackComponent={ErrorPage}>
            <Suspense fallback={<FullScreenLoadingSpinner/>}>
                <Outlet/>
            </Suspense>
        </ErrorBoundary>
    );
};

const ProjectRouter = (): JSX.Element => {
    const [client] = useState(new QueryClient());
    const router = createBrowserRouter([
        {
            path: "/",
            element: <Root/>,
            errorElement: <FourOhFour/>,
            children: [...routes],
        },
    ]);

    return (
        <QueryClientProvider client={client}>
            <RouterProvider router={router}/>
        </QueryClientProvider>
    );
};

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
    <React.StrictMode>
        <ProjectRouter/>
    </React.StrictMode>,
);