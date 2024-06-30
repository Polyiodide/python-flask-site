function opener() {
    const acc = document.getElementById("account");
    const menu = document.getElementById("menu");
    if (!!acc) {
        acc.onmouseenter = function () {menu.classList.add("MenuOpened");};
        menu.onmouseleave = function () {menu.classList.remove("MenuOpened");};
    }
}

function sure() {
    elems = document.querySelectorAll(".confirm");
    for (var i = 0; i < elems.length; i++) {
        console.log(elems[i], 'item')
        elems[i].onclick = function () {return confirm('Are you sure?')}
    }
}

onload = function () {
    opener();
    sure();
}