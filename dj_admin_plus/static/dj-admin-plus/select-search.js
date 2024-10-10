function createSelectTemplate(id) {
    return `
       <div id="${id}">
        <div style="margin-bottom: 8px">
            <input class="select-search" name="Search here" placeholder="Search here..." style="padding: 8px; border-radius: 8px">
            <button class="search-button" type="button" style="margin-left: 4px; background: blue; color: white; border: 2px solid blue; border-radius: 8px; padding: 4px 10px;">Search</button>
        </div>
        
        <div style="margin-bottom: 8px">
            <ul class="selected-items">
            </ul>
        </div>
    `
}

function elementSearchMatch(text, query) {
    // Normalize the text and query to lower case for case insensitive comparison
    const normalizedText = text.toLowerCase();
    const normalizedQuery = query.toLowerCase().trim();

    // Split the query into terms
    const terms = normalizedQuery.split(/\s+/); // Split by whitespace

    // Allow for wildcard matching using an asterisk (*) at the start or end
    const modifiedTerms = terms.map(term => term.replace(/\*/g, '')); // Remove wildcards

    // Check for partial matches, allowing for emojis
    return modifiedTerms.every(term => {
        // Check if the term is contained in the text, allowing for partial matches
        return normalizedText.includes(term);
    });
}

function displaySelectedElements(selectElement, displayElement) {
    // Clear display elements
    displayElement.innerHTML = "";

    // Load selected elements
    const options = selectElement.querySelectorAll("option");
    options.forEach(option => {
        if (option.selected) {
            displayElement.insertAdjacentHTML("afterbegin", `<li style="margin-top: 8px">${option.innerText}</li>`);
        }
    });
}

function loadSearch(selectElement, originalOptionsHtml, query) {
    selectElement.innerHTML = originalOptionsHtml;
    let options = selectElement.querySelectorAll("option");
    if (query.length === 0) {
        return;
    }

    options.forEach(option => {
        if (!(elementSearchMatch(option.value, query) || elementSearchMatch(option.innerHTML, query))) {
            option.remove();
        }
    });
}

function modifyElements(element) {
    element.style.display = 'none';
    const originalOptionsHtml = element.innerHTML;

    const id = crypto.randomUUID();
    element.insertAdjacentHTML('beforebegin', createSelectTemplate(id));

    let selectDivContainer = document.getElementById(id.toString());
    let selectedItemsDiv = selectDivContainer.querySelector('.selected-items');
    displaySelectedElements(element, selectedItemsDiv);

    const selectSearchElement = document.getElementsByClassName("select-search")[0];
    document.addEventListener("click", event => {
        const targetElement = event.target;
        if (targetElement === selectSearchElement || element.contains(targetElement) ||
            selectDivContainer.contains(targetElement)) {
            element.style.display = 'block';
        } else {
            element.style.display = 'none';
        }
    });

    const searchButton = document.getElementsByClassName("search-button")[0];

    selectSearchElement.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            loadSearch(element, originalOptionsHtml, selectSearchElement.value);
        }
    });

    searchButton.addEventListener('click', event => {
        event.preventDefault();
        loadSearch(element, originalOptionsHtml, selectSearchElement.value);
    });

    // Handle select changes
    element.addEventListener('change', _event => {
        displaySelectedElements(element, selectedItemsDiv);
    });
}

// Disable default select
const styleTag = document.createElement('style');
styleTag.innerHTML = `select {display: none}`;
document.head.innerHTML += styleTag;

window.onload = function () {
    const selectElements = document.getElementsByTagName("select");
    for (let i = 0; i < selectElements.length; i++) {
        const selectElement = selectElements[i];
        modifyElements(selectElement);
    }
}
