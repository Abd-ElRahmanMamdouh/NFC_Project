// Back to top
var scrollToTopBtn = document.querySelector('#scrollToTopBtn');
var rootElement = document.documentElement;
var scrollTotal = rootElement.scrollHeight - rootElement.clientHeight;
var rootElement = document.documentElement;

function handleScroll() {
    var scrollTotal = rootElement.scrollHeight - rootElement.clientHeight;
    if ((rootElement.scrollTop / scrollTotal) > 0.80) {
        scrollToTopBtn.classList.add("showBtn")
    } else {
        scrollToTopBtn.classList.remove("showBtn")
    }
};
document.addEventListener("scroll", handleScroll);

// Preloader
document.onreadystatechange = function() {
    if (document.readyState !== "complete") {
        document.querySelector("body").style.visibility = "hidden";
        document.querySelector("#preloader").style.visibility = "visible";
    } else {
        document.querySelector("#preloader").style.display = "none";
        document.querySelector("body").style.visibility = "visible";
    };
};
