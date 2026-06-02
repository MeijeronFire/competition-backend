// SPDX - License - Identifier: GPL - 3.0 - or - later
// Copyright(C) 2026 Otto Crawford

document.addEventListener('alpine:init', () => {
    Alpine.store('users', {
        // like dict unpacking in python, so you can access a card with $store.cards.<cardID>
        ...(window.initialJSON || {})
    });
});

const events = new EventSource(`/stream/${window.roomID}`);

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

    console.log(msg)

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
