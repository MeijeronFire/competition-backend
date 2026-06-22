// SPDX - License - Identifier: GPL - 3.0 - or - later
// Copyright(C) 2026 Otto Crawford

// TODO: add documentation to show what the users object looks like

document.addEventListener('alpine:init', () => {
    Alpine.store('users', {
        // like dict unpacking in python, so you can access a card with $store.users.<user UUID>
        ...(window.initialJSON || {})
    });
});

const events = new EventSource(`/stream/${window.roomID}`);

let before = [0, 0, 0, 0, 0, 0];

events.onmessage = async (event) => {
    // terrible code but it is objectively funny to access:
    // newcard = data.data = data.data.data
    let msg;
    try {
        msg = JSON.parse(JSON.parse(event.data).data);
    } catch (error) {
        console.warn("Received invalid json, skipping")
        return;
    }

    // console.log(msg)

    switch (msg.type) {
        case "newPlayer":
            let updateList = msg.data
            Alpine.store('users')[updateList.UUID] = updateList
            break;
        case "delPlayer":
            delete Alpine.store('users')[msg.data.UUID]
            break;
        case "glassesEvent":
            let after = msg.data;
            const changes = before.flatMap((v, i) =>
                v !== after[i]
                    ? [{ index: i, diff: after[i] - v }]
                    : []
            );

            // console.log(changes);
            before = [...after];
            for (const x of changes) {
                if (x.diff === 0) continue;
                await console.log(x.index, x.diff);
            }
            break;
        default:
            return;
    }
};

window.updateRoom = async function updateRoom(action) {
    if (!["open", "close", "start", "stop", "reset"].includes(action)) {
        throw new Error("Chose a command that does not exist.");
        return;
    }

    // now we know the ID is valid
    console.log(`requested game state update at ${window.roomID}`)
    const resp = await csrfFetch(`/api/room-${window.roomID}/state-${action}`, { method: "POST" });
    if (!resp.ok) {
        warn("Reloading the page will probably fix the issue. If not, contact maintainer.", "Invalid request")
    }
}

window.kickPlayer = async function kickPlayer(UUID) {
    if (!(UUID in Alpine.store('users'))) {
        throw ("Player UUID provided that does not exist");
        return;
    }
    // now we know the ID is valid
    console.log(`requested player kick of player ${UUID}, named ${Alpine.store('users')[UUID].name}`)
    const resp = await csrfFetch(`/api/room-${window.roomID}/playerOperation`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            action: "kick",
            targetPlayerUUID: UUID
        })
    });
    if (!resp.ok) {
        warn("Reloading the page will probably fix the issue. If not, contact maintainer.", "Invalid request")
    }
}