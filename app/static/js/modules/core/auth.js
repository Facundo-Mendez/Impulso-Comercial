class Auth {
  constructor(){ this._token = sessionStorage.getItem('token') || null; this.user = null; }
  setToken(t){ this._token = t; t ? sessionStorage.setItem('token', t) : sessionStorage.removeItem('token'); }
  get token(){ return this._token; }
  isLogged(){ return !!this._token; }
}
export const auth = new Auth();
