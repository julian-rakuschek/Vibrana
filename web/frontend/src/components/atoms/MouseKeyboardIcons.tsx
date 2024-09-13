import React from 'react';
import type { SVGProps } from 'react';

export function MouseScroll(props: SVGProps<SVGSVGElement>) {
	return (<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" {...props}><path fill="currentColor" d="m12 5l.53-.53a.75.75 0 0 0-1.06 0zm0 8l-.53.53a.75.75 0 0 0 1.06 0zM9.47 6.47a.75.75 0 0 0 1.06 1.06zm4 1.06a.75.75 0 1 0 1.06-1.06zm-2.94 2.94a.75.75 0 1 0-1.06 1.06zm4 1.06a.75.75 0 1 0-1.06-1.06zM3.25 10v4h1.5v-4zm17.5 4v-4h-1.5v4zm-9.5-9v8h1.5V5zm.22-.53l-2 2l1.06 1.06l2-2zm0 1.06l2 2l1.06-1.06l-2-2zm1.06 6.94l-2-2l-1.06 1.06l2 2zm0 1.06l2-2l-1.06-1.06l-2 2zM20.75 10A8.75 8.75 0 0 0 12 1.25v1.5A7.25 7.25 0 0 1 19.25 10zM12 22.75A8.75 8.75 0 0 0 20.75 14h-1.5A7.25 7.25 0 0 1 12 21.25zM3.25 14A8.75 8.75 0 0 0 12 22.75v-1.5A7.25 7.25 0 0 1 4.75 14zm1.5-4A7.25 7.25 0 0 1 12 2.75v-1.5A8.75 8.75 0 0 0 3.25 10z"></path></svg>);
}


export function MouseButtonLeft(props: SVGProps<SVGSVGElement>) {
	return (<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" {...props}><g fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth={1.5}><path d="M20 10v4a8 8 0 1 1-16 0V9a7 7 0 0 1 7-7h1a8 8 0 0 1 8 8Z"></path><path d="M12 2v6.4a.6.6 0 0 1-.6.6H4"></path></g></svg>);
}

export function MouseButtonRight(props: SVGProps<SVGSVGElement>) {
	return (<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" {...props}><g fill="none" stroke="currentColor" strokeLinecap="round" strokeWidth={1.5}><path d="M4 10v4a8 8 0 1 0 16 0V9a7 7 0 0 0-7-7h-1a8 8 0 0 0-8 8Z"></path><path d="M12 2v6.4a.6.6 0 0 0 .6.6H20"></path></g></svg>);
}


export function ShiftKey(props: SVGProps<SVGSVGElement>) {
	return (<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 24 24" {...props}><g fill="none" stroke="currentColor" strokeWidth={1.5}><path d="M3 19V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"></path><path strokeLinecap="round" strokeLinejoin="round" d="m8 14l4-4l4 4"></path></g></svg>);
}

export function VaadinShift(props: SVGProps<SVGSVGElement>) {
	return (<svg xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 16 16" {...props}><path fill="currentColor" d="M0 2v12h16V2zm6 6v3H4V8H2l3-3l3 3z"></path></svg>);
}