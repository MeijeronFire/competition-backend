// SPDX - License - Identifier: GPL - 3.0 - or - later
// Copyright(C) 2026 Otto Crawford

function canonicalize(value) {
    if (value instanceof Map) {
        return Object.fromEntries(
            [...value.entries()]
                .sort(([a], [b]) => String(a).localeCompare(String(b)))
                .map(([k, v]) => [k, canonicalize(v)])
        );
    }

    if (Array.isArray(value)) {
        return value.map(canonicalize);
    }

    if (value && typeof value === "object") {
        return Object.fromEntries(
            Object.keys(value)
                .sort()
                .map(key => [key, canonicalize(value[key])])
        );
    }

    return value;
}

function canonicalJSONStringify(value) {
    return JSON.stringify(canonicalize(value));
}

async function hashCanonicalJSON(value) {
    const json = canonicalJSONStringify(value);

    const bytes = new TextEncoder().encode(json);

    const hashBuffer = await crypto.subtle.digest("SHA-256", bytes);

    return [...new Uint8Array(hashBuffer)]
        .map(b => b.toString(16).padStart(2, "0"))
        .join("");
}