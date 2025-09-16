export class ApiClient {
  constructor({ baseUrl = '/api', getToken, onAuthError, onRateLimit } = {}){
    this.baseUrl = baseUrl;
    this.getToken = getToken;
    this.onAuthError = onAuthError;
    this.onRateLimit = onRateLimit;
  }
  async request(path, { method='GET', body, headers } = {}){
    const h = { 'Content-Type':'application/json', ...(headers||{}) };
    const token = this.getToken?.();
    if (token) h['Authorization'] = `Bearer ${token}`;
    const res = await fetch(`${this.baseUrl}${path}`, { method, headers:h, body: body? JSON.stringify(body): undefined });
    if (res.status === 401){ this.onAuthError?.(); throw new Error('No autorizado'); }
    if (res.status === 429){ this.onRateLimit?.(res); throw new Error('Rate limit'); }
    if (!res.ok){ const msg = await res.text(); throw new Error(msg || 'Error de servidor'); }
    const ct = res.headers.get('Content-Type') || '';
    return ct.includes('application/json') ? res.json() : res.text();
  }
  get(p){ return this.request(p); }
  post(p,b){ return this.request(p,{method:'POST', body:b}); }
  put(p,b){ return this.request(p,{method:'PUT', body:b}); }
  del(p){ return this.request(p,{method:'DELETE'}); }
}
