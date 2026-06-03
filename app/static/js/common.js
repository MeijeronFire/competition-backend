// SPDX - License - Identifier: GPL - 3.0 - or - later
// Copyright(C) 2026 Otto Crawford

// flashing a warning if something is wrong
function warn(msg, title = "Error") {
    const warning = document.createElement("div");
    warning.className = "alert alert-warning alert-dismissible";
    warning.role = "alert";
    warning.innerHTML = `
        <h4 class="alert-heading mt-0">${title}</h4>
        ${msg}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.getElementById("alert-container").appendChild(warning);
}

// patched version of fetch to include CSRF token
function csrfFetch(url, options = {}) {
    const method = (options.method || "GET").toUpperCase();

    const headers = new Headers(options.headers || {});

    if (method === "POST") {
        headers.set("X-CSRF-Token", window.CSRF_TOKEN);
    }

    return fetch(url, {
        ...options,
        headers
    });
}