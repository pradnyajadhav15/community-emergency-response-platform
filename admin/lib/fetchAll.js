import api from "./api";

// Follows DRF pagination links and returns every result.
export async function fetchAll(path, maxPages = 20) {
  const out = [];
  let url = path;
  for (let i = 0; i < maxPages && url; i++) {
    const { data } = await api.get(url);
    if (Array.isArray(data)) return data;
    out.push(...data.results);
    url = data.next ? data.next.replace(/^.*\/api/, "") : null;
  }
  return out;
}