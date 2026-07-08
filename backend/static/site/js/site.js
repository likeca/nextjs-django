(function () {
    let top = window.scrollY;
    if (top < 40) {
        document.getElementById("mainNav").classList.remove("bg-light");
        document.getElementById("mainNav").classList.remove("shadow");
    }

    window.onscroll = function () {
        top = window.scrollY;
        if (top < 40) {
            document.getElementById("mainNav").classList.remove("bg-light");
            document.getElementById("mainNav").classList.remove("shadow");
        } else {
            document.getElementById("mainNav").classList.add("bg-light");
            document.getElementById("mainNav").classList.add("shadow");
        }
    };
})();