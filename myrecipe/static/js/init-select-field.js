// Init Materialize select field - dietary tags
document.addEventListener('DOMContentLoaded', function () {
    let select = document.querySelectorAll('select');
    M.FormSelect.init(select);

    document.getElementsByClassName("select-dropdown")[0].placeholder = "Add dietary filters";
});