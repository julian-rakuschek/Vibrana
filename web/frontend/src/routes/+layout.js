export const ssr = false;

export async function load() {
  const res = await fetch('/api/config');
  const config = await res.json();
  return { config };
}
