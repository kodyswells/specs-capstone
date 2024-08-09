
function toggleFilter(filterId) {
    var filter = document.getElementById(filterId);
    if (filter.style.display === "none" || filter.style.display === "") {
        filter.style.display = "block";
    } else {
        filter.style.display = "none";
    }
}