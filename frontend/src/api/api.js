// Dito pinipili kung alin ang gagamitin ng app:
//   - http.js: totoong Django backend (default)
//   - mock.js: demo na walang backend, nakasave sa browser (VITE_USE_MOCK=true)
import * as http from './http.js';
import * as mock from './mock.js';

const impl = import.meta.env.VITE_USE_MOCK === 'true' ? mock : http;

export const CATEGORIES = impl.CATEGORIES;
export const currentUser = impl.currentUser;
export const login = impl.login;
export const logout = impl.logout;
export const listItems = impl.listItems;
export const getItem = impl.getItem;
export const createItem = impl.createItem;
export const updateItem = impl.updateItem;
export const deleteItem = impl.deleteItem;
export const submitClaim = impl.submitClaim;
export const listClaims = impl.listClaims;
export const decideClaim = impl.decideClaim;
