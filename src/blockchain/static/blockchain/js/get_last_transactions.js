let list = document.getElementById('last-transactions');

fetch('/get-last-transactions/')
.then(response => response.json())
.then(data => {
    if(data === 'Нет транзакций...') {
        let elem = document.createElement('li');
        elem.textContent = data;
        list.appendChild(elem);
    } else {
        for (let text of data) {
            let elem = document.createElement('li');
            let words = text.split(' ').map(word => word.replace('|', ' '));
            let formattedText = words.join('<br>');
            elem.innerHTML = formattedText;
            list.appendChild(elem);
        }
    }
})