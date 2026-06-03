// SPDX - License - Identifier: GPL - 3.0 - or - later
// Copyright(C) 2026 Otto Crawford

// I HATE VANILLA JS. WHY IS THERE NO NORMAL DOM MANIPULATION?
// thank god for alpine

document.addEventListener('alpine:init', () => {
    Alpine.store('cards', {
        // like dict unpacking in python, so you can access a card with $store.cards.<cardID>
        ...(window.initialCards || {})
    });
});

const events = new EventSource("/stream/dashboard");

events.onmessage = (event) => {
    // terrible code but it is objectively funny to access:
    // newcard = data.data = data.data.data
    let msg;

    try {
        msg = JSON.parse(JSON.parse(event.data).data);
    } catch (error) {
        console.warn("Received invalid json, skipping")
        return;
    }

    switch (msg.type) {
        case "update":
            let updateCard = msg.data
            Alpine.store('cards')[updateCard.id] = updateCard
            break;
        case "delete":
            delete Alpine.store('cards')[msg.data.id]
            break;
        case "create":
            let newCard = msg.data
            Alpine.store('cards')[newCard.id] = newCard
            break;
        default:
            return;
    }
};

// functions to handle dashboard actions
async function rmGame(cardID) {
    if (!(cardID in Alpine.store('cards'))) {
        throw ("Card ID provided that does not exist");
        return;
    }
    // now we know the ID is valid
    console.log(`requested deletion at ${cardID}`)
    const resp = await csrfFetch("/api/delRoom", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            roomID: cardID
        })
    });
    if (!resp.ok) {
        warn("reloading the page will probably fix the issue. If not, contact maintainer.", "Invalid request")
    }
}

async function createGame(gameName) {
    console.log(`requested new game name ${gameName}`)
    csrfFetch("/api/createRoom", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            gameName: gameName
        })
    });
}