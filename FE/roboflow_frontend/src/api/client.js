    const BASE =
      (process.env.REACT_APP_API_BASE || 'http://k13e103.p.ssafy.io').replace(/\/+$/, '');
    const getJson = async (path, params = {}) => {
      const url = new URL(`${BASE}${path}`);
      Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v);
      });
    
      const res = await fetch(url.toString(), {
        method: 'GET',
        headers: { Accept: 'application/json' },
      });
    
      if (!res.ok) {
        const text = await res.text().catch(() => '');
        throw new Error(`GET ${url} -> ${res.status} ${res.statusText}\n${text}`);
      }
      return res.json();
    };

    // default + named 둘 다 제공 (모듈 해석/캐시 엣지 케이스 방지)
    export default getJson;
    export { getJson };
