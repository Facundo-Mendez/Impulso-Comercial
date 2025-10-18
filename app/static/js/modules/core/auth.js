class Auth {
  constructor(){ this._token = localStorage.getItem('token') || null; this.user = null; }
  setToken(t){ this._token = t; t ? localStorage.setItem('token', t) : localStorage.removeItem('token'); }
  get token(){ return this._token; }
  isLogged(){ return !!this._token; }
}
export const auth = new Auth();