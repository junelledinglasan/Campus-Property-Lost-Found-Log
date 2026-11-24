// MOCK API: para sa demo na walang Django backend.
// Ang data ay nakasave sa localStorage ng browser, kaya mawawala kapag nilinis ang browser data.
// Ginagamit lang ito kapag VITE_USE_MOCK=true. Ang totoong koneksyon sa Django ay nasa http.js.

const DB_KEY = 'lf_db_v1';
const SESSION_KEY = 'lf_session_v1';

export const CATEGORIES = [
  'Wallet and cards',
  'ID and documents',
  'Bag',
  'Phone and gadgets',
  'Keys',
  'Clothing',
  'Books and school supplies',
  'Water bottle and tumbler',
  'Other',
];

// Demo account lang ito para sa prototype. Papalitan ng totoong login sa Django.
const DEMO_STAFF = { username: 'osas', password: 'osas123', displayName: 'OSAS Staff' };

const sleep = (ms = 150) => new Promise((r) => setTimeout(r, ms));

const daysAgo = (n) => {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
};

function seed() {
  return {
    nextItemId: 7,
    nextClaimId: 1,
    claims: [],
    items: [
      { id: 1, name: 'Black leather wallet', category: 'Wallet and cards', description: 'Folded wallet with a worn corner. Has a few cards inside.', photo: null, dateFound: daysAgo(1), placeFound: 'Library, 2nd floor', status: 'Unclaimed' },
      { id: 2, name: 'Blue umbrella with wooden handle', category: 'Other', description: 'Large folding umbrella, navy blue, with a loop strap.', photo: null, dateFound: daysAgo(2), placeFound: 'Canteen', status: 'Unclaimed' },
      { id: 3, name: 'Scientific calculator', category: 'Books and school supplies', description: 'Casio fx-991, name sticker peeled off the back.', photo: null, dateFound: daysAgo(3), placeFound: 'Room 204', status: 'Unclaimed' },
      { id: 4, name: 'Set of keys with green lanyard', category: 'Keys', description: 'Three keys on a green lanyard with a small bear keychain.', photo: null, dateFound: daysAgo(5), placeFound: 'Main gate', status: 'Unclaimed' },
      { id: 5, name: 'Gray hoodie, size M', category: 'Clothing', description: 'Plain gray pullover hoodie, left on a bench.', photo: null, dateFound: daysAgo(6), placeFound: 'Covered court', status: 'Unclaimed' },
      { id: 6, name: 'White earbuds in charging case', category: 'Phone and gadgets', description: 'White wireless earbuds with a clear case.', photo: null, dateFound: daysAgo(9), placeFound: 'Computer lab 3', status: 'Unclaimed' },
    ].map((i) => ({ ...i, createdAt: new Date().toISOString() })),
  };
}

function load() {
  try {
    const raw = localStorage.getItem(DB_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    /* gagamit ng seed data */
  }
  const db = seed();
  save(db);
  return db;
}

function save(db) {
  try {
    localStorage.setItem(DB_KEY, JSON.stringify(db));
  } catch {
    throw new Error('The browser storage is full. Use a smaller photo or delete old records.');
  }
}

// ---------- Auth ----------

export function currentUser() {
  try {
    return JSON.parse(sessionStorage.getItem(SESSION_KEY));
  } catch {
    return null;
  }
}

function requireStaff() {
  if (!currentUser()) throw new Error('Sign in as OSAS staff to do this.');
}

export async function login(username, password) {
  await sleep();
  if (username.trim() === DEMO_STAFF.username && password === DEMO_STAFF.password) {
    const user = { username: DEMO_STAFF.username, displayName: DEMO_STAFF.displayName };
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(user));
    return user;
  }
  throw new Error('Wrong username or password.');
}

export function logout() {
  sessionStorage.removeItem(SESSION_KEY);
}

// ---------- Items ----------

export async function listItems() {
  await sleep();
  return load().items;
}

export async function getItem(id) {
  await sleep();
  const db = load();
  const item = db.items.find((i) => i.id === Number(id));
  if (!item) throw new Error('This item does not exist or was removed.');
  // Proof na naibalik na: ang handover photo ng inaprubahang claim, walang pangalan.
  const claim = item.status === 'Claimed' ? db.claims.find((c) => c.itemId === item.id && c.status === 'Approved') : null;
  return { ...item, handoverPhoto: claim ? claim.handoverPhoto : null, returnedAt: claim ? claim.decidedAt : null };
}

function cleanItemInput(data) {
  const name = (data.name || '').trim();
  if (!name) throw new Error('Enter the item name.');
  if (!data.placeFound || !data.placeFound.trim()) throw new Error('Enter where the item was found.');
  if (!data.dateFound) throw new Error('Enter the date the item was found.');
  return {
    name,
    category: data.category || 'Other',
    description: (data.description || '').trim(),
    photo: data.photo || null,
    dateFound: data.dateFound,
    placeFound: data.placeFound.trim(),
  };
}

export async function createItem(data) {
  await sleep();
  requireStaff();
  const db = load();
  const item = {
    id: db.nextItemId++,
    ...cleanItemInput(data),
    status: 'Unclaimed',
    createdAt: new Date().toISOString(),
  };
  db.items.push(item);
  save(db);
  return item;
}

export async function updateItem(id, data) {
  await sleep();
  requireStaff();
  const db = load();
  const item = db.items.find((i) => i.id === Number(id));
  if (!item) throw new Error('This item does not exist or was removed.');
  Object.assign(item, cleanItemInput(data));
  save(db);
  return item;
}

export async function deleteItem(id) {
  await sleep();
  requireStaff();
  const db = load();
  db.items = db.items.filter((i) => i.id !== Number(id));
  db.claims = db.claims.filter((c) => c.itemId !== Number(id));
  save(db);
}

// ---------- Claims ----------

const STUDENT_NO = /^[A-Za-z0-9-]{4,20}$/;

export async function submitClaim({ itemId, fullName, studentNo }) {
  await sleep();
  const name = (fullName || '').trim().replace(/\s+/g, ' ');
  const no = (studentNo || '').trim();
  if (name.split(' ').length < 2) throw new Error('Enter your full name, first and last.');
  if (!STUDENT_NO.test(no)) throw new Error('Enter a valid student number (letters, numbers, and dashes only).');

  const db = load();
  const item = db.items.find((i) => i.id === Number(itemId));
  if (!item) throw new Error('This item does not exist or was removed.');
  if (item.status !== 'Unclaimed') throw new Error('This item can no longer be claimed.');

  const claim = {
    id: db.nextClaimId++,
    itemId: item.id,
    fullName: name,
    studentNo: no,
    submittedAt: new Date().toISOString(),
    status: 'Pending',
    verifiedName: null,
    verifiedStudentNo: null,
    handoverPhoto: null,
    decidedAt: null,
    decidedBy: null,
  };
  db.claims.push(claim);
  item.status = 'Pending';
  save(db);
  return { id: claim.id };
}

export async function listClaims() {
  await sleep();
  requireStaff();
  const db = load();
  return db.claims
    .map((c) => {
      const item = db.items.find((i) => i.id === c.itemId);
      return { ...c, itemName: item ? item.name : 'Removed item', itemPhoto: item ? item.photo : null };
    })
    .sort((a, b) => b.submittedAt.localeCompare(a.submittedAt));
}

export async function decideClaim(id, { decision, verifiedName, verifiedStudentNo, handoverPhoto }) {
  await sleep();
  requireStaff();
  const db = load();
  const claim = db.claims.find((c) => c.id === Number(id));
  if (!claim) throw new Error('This claim does not exist.');
  if (claim.status !== 'Pending') throw new Error('This claim was already decided.');
  const item = db.items.find((i) => i.id === claim.itemId);

  const name = (verifiedName || '').trim();
  const no = (verifiedStudentNo || '').trim();
  if (!name || !no) throw new Error('Enter the name and student number shown on the ID.');

  if (decision === 'Approved') {
    if (!handoverPhoto) throw new Error('Add the handover photo before approving.');
    if (item) item.status = 'Claimed';
  } else if (item) {
    item.status = 'Unclaimed';
  }

  Object.assign(claim, {
    status: decision,
    verifiedName: name,
    verifiedStudentNo: no,
    handoverPhoto: decision === 'Approved' ? handoverPhoto : null,
    decidedAt: new Date().toISOString(),
    decidedBy: currentUser().displayName,
  });
  save(db);
  return claim;
}
