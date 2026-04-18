// ============================================
// CONFIG — Change this URL for production
// ============================================
const API_URL = "http://127.0.0.1:8000";

// ============================================
// DOM REFERENCES
// ============================================
const $  = (s) => document.querySelector(s);
const authPage      = $("#auth-page");
const dashPage      = $("#dashboard-page");
const authEmail     = $("#auth-email");
const authPassword  = $("#auth-password");
const authError     = $("#auth-error");
const btnLogin      = $("#btn-login");
const btnRegister   = $("#btn-register");
const btnLogout     = $("#btn-logout");
const userEmailSpan = $("#user-email");
const bmForm        = $("#bookmark-form");
const formTitle     = $("#form-title");
const editIdInput   = $("#edit-id");
const bmTitle       = $("#bm-title");
const bmUrl         = $("#bm-url");
const bmDesc        = $("#bm-desc");
const bmTags        = $("#bm-tags");
const btnSave       = $("#btn-save");
const btnCancel     = $("#btn-cancel");
const bookmarkList  = $("#bookmark-list");
const emptyState    = $("#empty-state");
const loadingEl     = $("#loading");
const toastEl       = $("#toast");

// ============================================
// HELPERS
// ============================================
function getToken() { return localStorage.getItem("jwt_token"); }
function setToken(t) { localStorage.setItem("jwt_token", t); }
function removeToken() { localStorage.removeItem("jwt_token"); }

// Decode a JWT payload (base64) to read the user info — no library needed
function decodeToken(token) {
    try {
        const payload = token.split(".")[1];
        return JSON.parse(atob(payload));
    } catch { return null; }
}

let toastTimer;
function showToast(msg, type = "success") {
    clearTimeout(toastTimer);
    toastEl.textContent = msg;
    toastEl.className = "toast " + type + " show";
    toastTimer = setTimeout(() => { toastEl.classList.remove("show"); }, 3000);
}

async function api(path, options = {}) {
    const token = getToken();
    const headers = options.headers || {};
    if (token) headers["Authorization"] = "Bearer " + token;
    if (options.body && typeof options.body === "object" && !(options.body instanceof URLSearchParams)) {
        headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(options.body);
    }
    options.headers = headers;
    const res = await fetch(API_URL + path, options);
    if (res.status === 401) { removeToken(); showPage("auth"); throw new Error("Session expired"); }
    return res;
}

// ============================================
// NAVIGATION
// ============================================
function showPage(page) {
    authPage.classList.toggle("hidden", page !== "auth");
    dashPage.classList.toggle("hidden", page !== "dashboard");
    if (page === "auth") { authError.textContent = ""; }
}

function init() {
    if (getToken()) { showPage("dashboard"); loadBookmarks(); }
    else { showPage("auth"); }
}

// ============================================
// AUTH
// ============================================
btnRegister.addEventListener("click", async () => {
    authError.textContent = "";
    const email = authEmail.value.trim();
    const password = authPassword.value;
    if (!email || !password) { authError.textContent = "Please fill in all fields."; return; }
    try {
        btnRegister.disabled = true;
        const res = await api("/auth/register", { method: "POST", body: { email, password } });
        if (!res.ok) { const d = await res.json(); throw new Error(d.detail || "Registration failed"); }
        showToast("Account created! You can now login.", "success");
    } catch (e) { authError.textContent = e.message; }
    finally { btnRegister.disabled = false; }
});

btnLogin.addEventListener("click", async () => {
    authError.textContent = "";
    const email = authEmail.value.trim();
    const password = authPassword.value;
    if (!email || !password) { authError.textContent = "Please fill in all fields."; return; }
    try {
        btnLogin.disabled = true;
        const body = new URLSearchParams({ username: email, password });
        const res = await api("/auth/login", { method: "POST", body });
        if (!res.ok) { const d = await res.json(); throw new Error(d.detail || "Login failed"); }
        const data = await res.json();
        setToken(data.access_token);
        showToast("Welcome back!");
        showPage("dashboard");
        loadBookmarks();
    } catch (e) { authError.textContent = e.message; }
    finally { btnLogin.disabled = false; }
});

btnLogout.addEventListener("click", () => { removeToken(); showPage("auth"); });

// ============================================
// BOOKMARKS — LOAD
// ============================================
async function loadBookmarks() {
    loadingEl.classList.remove("hidden");
    emptyState.classList.add("hidden");
    bookmarkList.innerHTML = "";
    try {
        const res = await api("/bookmarks/");
        if (!res.ok) throw new Error("Failed to load");
        const bookmarks = await res.json();
        loadingEl.classList.add("hidden");
        if (bookmarks.length === 0) { emptyState.classList.remove("hidden"); return; }
        bookmarks.forEach((bm) => bookmarkList.appendChild(createCard(bm)));
    } catch (e) { loadingEl.classList.add("hidden"); showToast(e.message, "error"); }
}

function createCard(bm) {
    const card = document.createElement("div");
    card.className = "bookmark-card";
    card.dataset.id = bm.id;

    const tagsHtml = bm.tags.map(t => `<span class="tag-pill">${esc(t.name)}</span>`).join("");
    const descHtml = bm.description ? `<p class="bm-desc">${esc(bm.description)}</p>` : "";
    const date = new Date(bm.created_at).toLocaleDateString("en-GB", { day:"numeric", month:"short", year:"numeric" });

    card.innerHTML = `
        <div class="bm-header">
            <span class="bm-title">${esc(bm.title)}</span>
            <div class="bm-actions">
                <button class="btn btn-edit" onclick="startEdit(${bm.id})">Edit</button>
                <button class="btn btn-danger" onclick="deleteBookmark(${bm.id})">Delete</button>
            </div>
        </div>
        <a class="bm-url" href="${esc(bm.url)}" target="_blank" rel="noopener">${esc(bm.url)}</a>
        ${descHtml}
        <div class="bm-tags">${tagsHtml}</div>
        <div class="bm-meta">Added ${date}</div>`;
    return card;
}

function esc(s) {
    const d = document.createElement("div"); d.textContent = s; return d.innerHTML;
}

// ============================================
// BOOKMARKS — CREATE / UPDATE
// ============================================
bmForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = editIdInput.value;
    const title = bmTitle.value.trim();
    const url = bmUrl.value.trim();
    const description = bmDesc.value.trim() || null;
    const tags = bmTags.value.split(",").map(t => t.trim()).filter(Boolean);

    if (!title || !url) { showToast("Title and URL are required.", "error"); return; }

    btnSave.disabled = true;
    try {
        if (id) {
            // UPDATE
            const body = { title, url, description, tags };
            const res = await api(`/bookmarks/${id}`, { method: "PUT", body });
            if (!res.ok) { const d = await res.json(); throw new Error(d.detail || "Update failed"); }
            showToast("Bookmark updated!");
        } else {
            // CREATE
            const res = await api("/bookmarks/", { method: "POST", body: { title, url, description, tags } });
            if (!res.ok) { const d = await res.json(); throw new Error(d.detail || "Create failed"); }
            showToast("Bookmark created!");
        }
        resetForm();
        loadBookmarks();
    } catch (e) { showToast(e.message, "error"); }
    finally { btnSave.disabled = false; }
});

// ============================================
// BOOKMARKS — EDIT MODE
// ============================================
// Store fetched bookmarks so we can populate the form without extra API call
window.startEdit = async function(id) {
    try {
        const res = await api(`/bookmarks/${id}`);
        if (!res.ok) throw new Error("Not found");
        const bm = await res.json();
        editIdInput.value = bm.id;
        bmTitle.value = bm.title;
        bmUrl.value = bm.url;
        bmDesc.value = bm.description || "";
        bmTags.value = bm.tags.map(t => t.name).join(", ");
        formTitle.textContent = "Edit Bookmark";
        btnSave.textContent = "Update Bookmark";
        btnCancel.classList.remove("hidden");
        window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e) { showToast(e.message, "error"); }
};

btnCancel.addEventListener("click", resetForm);

function resetForm() {
    editIdInput.value = "";
    bmForm.reset();
    formTitle.textContent = "Add New Bookmark";
    btnSave.textContent = "Save Bookmark";
    btnCancel.classList.add("hidden");
}

// ============================================
// BOOKMARKS — DELETE
// ============================================
window.deleteBookmark = async function(id) {
    if (!confirm("Delete this bookmark?")) return;
    try {
        const res = await api(`/bookmarks/${id}`, { method: "DELETE" });
        if (!res.ok && res.status !== 204) throw new Error("Delete failed");
        showToast("Bookmark deleted!");
        loadBookmarks();
    } catch (e) { showToast(e.message, "error"); }
};

// ============================================
// BOOT
// ============================================
init();
