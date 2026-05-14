// step 1: we create a websocket connection
const ws = new WebSocket(`wss://${window.location.host}/ws/dashboard`)

// bind an onmessage
ws.onmessage = async (e) => {
    const msg = JSON.parse(e.data);
    // the message we got
    // console.log(e.data)
    switch (msg.type) {
        case "create":
            addCard(msg.data)
            break;
        case "fullState":
            // first clear all cards
            clearCards();

            // then create all new ones
            for (const [key, value] of Object.entries(msg.data)) {
                addCard(value);
            }
            break;
        case "delete":
            removeCard(msg.data)
            break;
        default:
            console.log("warning: incomming ws message cannot be parsed")
            break;
    }
    // compare to the hash we have computed
    const hash = await hashCanonicalJSON(localState.cards)
    // now if they differ we call again
    if (hash != msg.stateHash && msg.type != "fullState") {
        console.log(`requesting again, ${hash} != ${msg.stateHash}, ${msg.stateHash != hash}`)
        await ws.send(JSON.stringify({
            action: "getState",
            data: {}
        }));
    }
};

function sleep(time) {
    return new Promise((resolve) => setTimeout(resolve, time));
}

async function register() {
    await sleep(250);
    await ws.send(JSON.stringify({
        csrf: window.CSRF_TOKEN
    }));
    await getTotalState();
}

async function getTotalState() {
    await ws.send(JSON.stringify({
        action: "getState",
        data: {}
    }));
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

/////////////////////////////////////////////////////////////////////
// abstract dealing with global state and rendering cards
// the local state looks like this:
/*
here any bootstrap color / border / badge is one of the following:
    "primary",
    "secondary",
    "success",
    "danger",
    "warning",
    "info",
    "light",
    "dark"
{
    <card-id (int)> : {
        "playerNr": <int>,
        "minPlayers": <int>,
        "title": <str>,
        "id": <id>,
        "gameState": <abstract representation of state>,
        "description": <str>,
        "borderType": <bootstrap border type (str)>
        "roomState": [
            {
                "type": <bootstrap badge type (str)>,
                "msg": <bootstrap badge msg (str)>
            }
        ]
    },
    <card-id (int)> : ...
}
*/
const localState = {
    cards: new Map() // id -> card data
};

const domMap = new Map(); // id -> DOM element

function addCard(cardJSON) {
    localState.cards.set(cardJSON.id, cardJSON);

    const card = createCard(cardJSON);
    domMap.set(cardJSON.id, card);

    document.getElementById("card-container").appendChild(card);
}

function updateCard(cardJSON) {
    // we get the ID of the card to be updated from the cardJSON, so
    // we only need one argument
    // first check if it exists
    oldCardJSON = localState.cards.get(cardJSON.id)
    if (!oldCardJSON) {
        console.log("Error! Provided card JSON does not exist -> can not be updated");
        return;
    }

    // update / overwrite part of the stored JSON itself
    Object.assign(oldCardJSON, cardJSON);

    card = domMap.get(cardJSON.id);
    if (!card) {
        console.log("Error! Provided card DOM element does not exist -> can not be updated");
        return;
    }
    parchCardDOM(card, cardJSON);
}

// delete the card by the JSON description of it
function removeCard(cardJSON) {
    // first delete it from the local state 
    localState.cards.delete(cardJSON.id);

    // then from the dom
    const card = domMap.get(cardJSON.id);
    if (card) {
        card.remove();
        domMap.delete(cardJSON.id);
    }
}

/////////////////////////////////////////////////////////////////////
// implementation of the abstract functions above
// create a card
function createCard(cardJSON) {
    const card = document.createElement("div");
    injectCardHTML(card, cardJSON);
    return card;
}

// patch / update a card. Takes card (DOM element) and the JSON description of it
function patchCardDOM(card, cardJSON) {
    injectCardHTML(card, cardJSON);
}

// delete a card

// enter the HTML for a card into an element of description `cardJSON'
function injectCardHTML(card, cardJSON) {
    card.className = "col-3";
    card.id = `card-${cardJSON.id}`;
    card.innerHTML = `
    <div class="card border-${cardJSON.borderType} mb-3">
        <div class="card-header">
        ${cardJSON.playerNr}/${cardJSON.minPlayers}
        ${cardJSON.roomState?.length
            ? cardJSON.roomState.map(badge => `
            <span class="badge rounded-pill bg-${badge.type}">${badge.msg}</span>
            `).join("")
            : ""
        }
        </div >
        <button class="btn-close position-absolute top-0 end-0 card-close" id="btn-${cardJSON.id}"></button>
        <div class="card-body">
            <h4 class="card-title">${cardJSON.title}</h4>
            <p class="card-text">${cardJSON.description}</p>
            <a href="/peek/${cardJSON.id}" class="btn btn-secondary w-100">Peek</a>
        </div>
    </div >
    `;
}

// clear all cards
function clearCards() {
    document.getElementById("card-container").innerHTML = "";
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
    // console.log(msg);
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