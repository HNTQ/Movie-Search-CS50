const search = document.querySelector("#mainSearch");
const filters = document.querySelectorAll("input[name='filter']");
const submit = document.querySelector("#submit_search");

search.addEventListener("keydown", e => {
    if (e.keyCode === 13) {
        e.preventDefault();
        isValidSearch(sendSearch);
    }
});

submit.addEventListener("click", e => {
    e.preventDefault();
    isValidSearch(sendSearch);
})

const sendSearch = () => {
    let hasFilters = false;
    let checkedFilters = [];
    filters.forEach(f => {
        if (f.checked) {
            hasFilters = true;
            checkedFilters.push(f.value);
        }
    });
    //const URI =
    window.location.assign(`/search?title=${encodeURI(search.value)}${hasFilters ? encodeURI(`&filter=${checkedFilters.join("+")}`) : ""}`);
}

const isValidSearch = (callback) => {
    if (search.value) {
        callback();
        return true;
    }
    return false;
}