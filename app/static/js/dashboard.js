// I HATE VANILLA JS. WHY IS THERE NO NORMAL DOM MANIPULATION?

document.addEventListener('alpine:init', () => {
    Alpine.store('cards', {
        items: Object.values(window.initialCards) || []
    });
});

const events = new EventSource("/stream/dashboard");

events.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(JSON.parse(data.data).data);
    Alpine.store('cards').items = [JSON.parse(data.data).data];
};

const state = {
    cards: window.initialCards || {}
};

function colorGen() {
    return ['red', 'green']
}