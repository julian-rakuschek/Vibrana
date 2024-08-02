import { useState } from "react";
import { Dialog, Popover } from "@headlessui/react";
import {Bars3Icon, XMarkIcon, DocumentIcon, CodeBracketIcon,} from "@heroicons/react/24/outline";
import { Link } from "react-router-dom";

export default function Navbar({ darkMode = false }: { darkMode?: boolean }): JSX.Element {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const menuLinks: { name: string; link: string }[] = [
    { name: "Entry1", link: "/entry1" },
    { name: "Entry2", link: "/entry2" },
    { name: "Entry3", link: "/entry3" },
  ];

  return (
    <header className={`${(darkMode) ? "bg-[#0e1b40]" : "bg-white"} z-50`}>
      <nav className="mx-auto flex max-w-7xl items-center justify-between p-6 lg:px-8" aria-label="Global">
        <div className="flex lg:flex-1">
          <Link to="/" className="-m-1.5 p-1.5">
            <span className={`${(darkMode) ? "text-white" : "text-black"} font-bold text-2xl`}>Project Name</span>
          </Link>
        </div>
        <div className="flex lg:hidden">
          <button
            type="button"
            className="-m-2.5 inline-flex items-center justify-center rounded-md p-2.5 text-gray-700"
            onClick={() => setMobileMenuOpen(true)}
          >
            <span className="sr-only">Open main menu</span>
            <Bars3Icon className="h-6 w-6" aria-hidden="true"/>
          </button>
        </div>
        <Popover.Group className="hidden lg:flex lg:gap-x-12">
          {menuLinks.map(menuLink =>
            <Link key={menuLink.link} to={menuLink.link} className={`text-sm font-semibold leading-6 ${(darkMode) ? "text-white before:border-b-white" : "text-gray-900 before:border-b-indigo-700"} border-animation`}>
              {menuLink.name}
            </Link>,
          )}
        </Popover.Group>
        <div className="hidden lg:flex lg:flex-1 lg:justify-end gap-x-4">
          <Link to="#" className={`text-sm font-semibold leading-6 ${(darkMode) ? "text-white before:border-b-white" : "text-gray-900 before:border-b-indigo-700"} flex flex-row items-center border-animation`}>
            <DocumentIcon className={`h-4 w-4 ${(darkMode) ? "text-white" : "text-gray-600"} mr-1`} /> Something
          </Link>
        </div>
      </nav>
      <div className="lg:hidden">
        <Dialog open={mobileMenuOpen} onClose={setMobileMenuOpen}>
          <div className="fixed inset-0 z-10"/>
          <Dialog.Panel className={`fixed inset-y-0 right-0 z-50 w-full overflow-y-auto ${(darkMode) ? "bg-[#0e1b40]" : "bg-white"} px-6 py-6 sm:max-w-sm sm:ring-1 sm:ring-gray-900/10`}>
            <div className="flex items-center justify-between">
              <Link to="/" className="-m-1.5 p-1.5">
                <span className="text-black font-bold text-2xl">Project Name</span>
              </Link>
              <button
                type="button"
                className="-m-2.5 rounded-md p-2.5 text-gray-700"
                onClick={() => setMobileMenuOpen(false)}
              >
                <span className="sr-only">Close menu</span>
                <XMarkIcon className="h-6 w-6" aria-hidden="true"/>
              </button>
            </div>
            <div className="mt-6 flow-root">
              <div className="-my-6 divide-y divide-gray-500/10">
                <div className="space-y-2 py-6">
                  {menuLinks.map(menuLink =>
                    <Link key={menuLink.link} to={menuLink.link} className={`-mx-3 block rounded-lg px-3 py-2 text-base font-semibold leading-7 ${(darkMode) ? "text-white" : "text-gray-900"}`}>{menuLink.name}</Link>,
                  )}
                </div>
                <div className="py-6">
                  <Link
                    to="#"
                    className={`-mx-3 rounded-lg px-3 py-2.5 text-base font-semibold leading-7 ${(darkMode) ? "text-white" : "text-gray-900"} flex flex-row items-center`}
                  >
                    <DocumentIcon className={`h-4 w-4 ${(darkMode) ? "text-white" : "text-gray-600"} mr-1`} /> Something
                  </Link>
                </div>
              </div>
            </div>
          </Dialog.Panel>
        </Dialog>
      </div>
    </header>
  );
}
