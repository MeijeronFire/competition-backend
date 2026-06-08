// SPDX - License - Identifier: GPL - 3.0 - or - later
// Copyright(C) 2026 Otto Crawford

document.addEventListener('alpine:init', () => {
    Alpine.store('users', {
        // like dict unpacking in python, so you can access a card with $store.cards.<cardID>
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

    console.log(msg)

    switch (msg.type) {
        case "newPlayer":
            let updateList = msg.data
            Alpine.store('users')[updateList.UUID] = updateList
            break;
        case "delPlayer":
            delete Alpine.store('users')[msg.data.UUID]
            break;
        case "create":
            let newCard = msg.data
            Alpine.store('cards')[newCard.id] = newCard
            break;
        case "glassesEvent":
            let after = msg.data;
            const changes = before.flatMap((v, i) =>
                v !== after[i]
                    ? [{ index: i, diff: after[i] - v }]
                    : []
            );

            console.log(changes);
            before = [...after];
            for (const x of changes) {
                if (x.diff === 0) continue;
                await fill(x.index, x.diff);
            }
        default:
            return;
    }
};

window.updateRoom = async function updateRoom(action) {
    if (!["open", "close", "start", "stop", "reset"].includes(action)) {
        throw new Error("Card ID provided that does not exist");
        return;
    }

    // now we know the ID is valid
    console.log(`requested game state update at ${window.roomID}`)
    const resp = await csrfFetch(`/api/room-${window.roomID}/${action}`, { method: "POST" });
    if (!resp.ok) {
        warn("Reloading the page will probably fix the issue. If not, contact maintainer.", "Invalid request")
    }
}

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const glassW = 120;
const glassH = 220;
const gap = 40;
const count = 6;

const totalWidth = count * glassW + (count - 1) * gap;
const startX = (canvas.width - totalWidth) / 2;
const startY = (canvas.height - glassH) / 2;

// state: fill levels per glass (0..1)
const fills = new Array(count).fill(0);

function drawGlass(ctx, x, y, w, h, fillPercent) {
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x + w, y);
    ctx.lineTo(x + w * 0.8, y + h);
    ctx.lineTo(x + w * 0.2, y + h);
    ctx.closePath();

    ctx.save();
    ctx.clip();

    const liquidHeight = h * fillPercent;

    ctx.fillStyle = "rgba(0, 120, 255, 0.5)";
    ctx.fillRect(
        x - 20,
        y + h - liquidHeight,
        w + 40,
        liquidHeight
    );

    ctx.restore();

    ctx.strokeStyle = "#333";
    ctx.lineWidth = 4;
    ctx.stroke();
}

function render() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < count; i++) {
        drawGlass(
            ctx,
            startX + i * (glassW + gap),
            startY,
            glassW,
            glassH,
            fills[i]
        );
    }
}

function fill(x, yPercent) {
    if (x < 0 || x >= count) return;

    const target = Math.max(0, Math.min(1, yPercent / 100));

    function animate() {
        const diff = target - fills[x];

        if (Math.abs(diff) < 0.002) {
            fills[x] = target;
            render();
            return;
        }

        fills[x] += diff * 0.1; // smoothing step
        render();
        requestAnimationFrame(animate);
        return;
    }

    animate();
    return;
}
// initial draw
render();
