// step 1: we create a websocket connection
const ws = new WebSocket(`wss://${window.location.host}/ws/dashboard`)

// bind an onmessage
ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);

    switch (msg.type) {
        case "create":
            console.log("created");
            createCard(msg.data)
            break;
        default:
            console.log("warning: incomming ws message cannot be parsed")
            break;
    }
};

async function register() {
    await sleep(250);
    await ws.send(JSON.stringify({
        csrf: window.CSRF_TOKEN
    }));
}

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

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

// create a card
function createCard(data) {
    const card = document.createElement("div");
    card.className = "col-3";
    card.id = `card-${data.id}`;
    card.innerHTML = `
    <div class="card border-primary mb-3">
        <div class="card-header">${data.playerNr}/${data.minPlayers}</div>
        <button class="btn-close position-absolute top-0 end-0 card-close" id="btn-${data.id}"></button>
        <div class="card-body">
            <h4 class="card-title">${data.title}</h4>
            <p class="card-text">Not quite sure what to put here just yet</p>
        </div>
    </div>
    `;

    document.getElementById("card-container").appendChild(card);
}

// get rid of a card
document.addEventListener("click", (e) => {
    // button = card-close closest to event `e'
    const button = e.target.closest(".card-close");
    if (!button) return;

    if (ws.readyState !== 1) {
        warn("Session invalid. Reload webpage.");
        return;
    }

    const id = button.id.replace("btn-", "");
    document.getElementById(`card-${id}`)?.remove();

    const msg = JSON.stringify({
        action: "delete",
        data: {
            roomID: id
        }
    });
    console.log(msg);
    ws.send(msg);
});

// dealing with creating new game!
document.addEventListener("click", (e) => {
    // element = ws option closest to event `e'
    const el = e.target.closest(".ws-option");
    if (!el) return;

    e.preventDefault();

    if (ws.readyState !== 1) {
        warn("Session invalid. Reload webpage.");
        return;
    }

    const msg = JSON.stringify({
        action: "create",
        data: {
            name: el.dataset.name
        }
    });
    console.log(msg);
    ws.send(msg);
});

register();