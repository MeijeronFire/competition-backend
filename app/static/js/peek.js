// step 1: we create a websocket connection
const ws = new WebSocket(`wss://${window.location.host}/ws/dashboard`)

// bind an onmessage
ws.onmessage = async (e) => {
    const msg = JSON.parse(e.data);
    // the message we got
    console.log(e.data)
    switch (msg.type) {
        case "fullRoomState":
            // first clear all cards
            clearItems();

            // then create all new ones
            for (const [key, value] of Object.entries(msg.data)) {
                addAccordionItem(value);
            }
            break;
        default:
            console.log("warning: incomming ws message cannot be parsed")
            return;
    }
    // compare to the hash we have computed
    // console.log(canonicalJSONStringify(localState))
    // console.log(canonicalJSONStringify(msg))
    // console.log(await hashCanonicalJSON(localState))
    const hash = await hashCanonicalJSON(localState)
    // now if they differ we call again
    if (hash != msg.stateHash) {
        console.log(`requesting again, ${hash} != ${msg.stateHash}, ${msg.stateHash != hash}`)
        // await ws.send(JSON.stringify({
        //     action: "getRoomState",
        //     data: {
        //         roomID: window.roomID
        //     }
        // }));
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
        action: "getRoomState",
        data: {
            roomID: window.roomID
        }
    }));
}

const localState = new Map(); // id -> card data

const domMap = new Map(); // id -> DOM element

function addAccordionItem(AccordionItemJSON) {
    localState.set(AccordionItemJSON.UUID, AccordionItemJSON);

    const item = createAccordionItem(AccordionItemJSON);
    domMap.set(AccordionItemJSON.UUID, item);

    document.getElementById("playernames").appendChild(item);
}

function updateItem(AccordionItemJSON) {
    // we get the ID of the card to be updated from the cardJSON, so
    // we only need one argument
    // first check if it exists
    // console.log(cardJSON)
    oldItemJSON = localState.get(AccordionItemJSON.UUID)
    if (!oldItemJSON) {
        console.log("Error! Provided accordion item JSON does not exist -> can not be updated");
        return;
    }

    // update / overwrite part of the stored JSON itself
    Object.assign(oldItemJSON, AccordionItemJSON);

    item = domMap.get(AccordionItemJSON.UUID);
    if (!item) {
        console.log("Error! Provided card DOM element does not exist -> can not be updated");
        return;
    }
    injectAccordianItemHTML(accordionItem, accordionItemJSON);
}

// delete the card by the JSON description of it
function removeItem(itemJSON) {
    // first delete it from the local state 
    localState.delete(itemJSON.UUID);

    // then from the dom
    const item = domMap.get(itemJSON.UUID);
    if (item) {
        item.remove();
        domMap.delete(itemJSON.UUID);
    }
}

/////////////////////////////////////////////////////////////////////
// implementation of the abstract functions above
// create a card
function createAccordionItem(accordionItemJSON) {
    const accordionItem = document.createElement("div");
    injectAccordianItemHTML(accordionItem, accordionItemJSON);
    return accordionItem;
}


// enter the HTML for a card into an element of description `cardJSON'
function injectAccordianItemHTML(accordionItem, accordionItemJSON) {
    accordionItem.className = "accordion-item";
    accordionItem.id = `card-${accordionItemJSON.UUID}`;
    accordionItem.innerHTML = `
            <h2 class="accordion-header">
                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse"
                    data-bs-target="#${accordionItemJSON.UUID}" aria-expanded="true" aria-controls="${accordionItemJSON.UUID}">
                    ${accordionItemJSON.name}
                </button>
            </h2>
            <div id="${accordionItemJSON.UUID}" class="accordion-collapse collapse" aria-labelledby="${accordionItemJSON.UUID}"
                data-bs-parent="#playernames">
                <div class="accordion-body">
                    content tbd
                </div>
            </div>
    `;
}

// clear all cards
function clearItems() {
    // TODO: remove everything except title of the accordion thingie
    document.getElementById("playernames").innerHTML = `
        <div class="accordion-item" id="title">
            <h3 class="accordion-header">
                Test
            </h2>
        </div>

    `;
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