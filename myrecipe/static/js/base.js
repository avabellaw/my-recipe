document.addEventListener('DOMContentLoaded', function () {
    let dropdowns = document.querySelectorAll('.dropdown-trigger');

    // Add dropdown options from stackoverflow [https://stackoverflow.com/questions/50051540/materialize-dropdown-options]
    let dropdownOptions = {
        // Make dropdown appear below dropdown trigger from stackoverflow [https://stackoverflow.com/questions/57773699/how-to-make-materializecss-dropdown-appear-below-selectbox]
        coverTrigger: false
    };

    M.Dropdown.init(dropdowns, dropdownOptions);

    let sidenavs = document.querySelectorAll('.sidenav');
    M.Sidenav.init(sidenavs, {
        edge: 'right', // Choose the horizontal origin
    });

    /*
        Decided to dismiss the flash message by clicking on the entire div rather than just the cross.
        The cross is there for visual feedback.
    */
    document.getElementById("flash-message").onclick = function () {
        this.style.display = "none";
    };

    // Scroll to search-form [https://stackoverflow.com/questions/31863582/automatically-scroll-to-a-div-when-flask-returns-rendered-template]
    document.location.hash = "#" + "{{ scroll }}";
});