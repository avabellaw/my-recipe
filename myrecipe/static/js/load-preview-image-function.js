// Load the function to show preview of uploaded images
function previewImage(event) {
    // Preview image before upload from StackOverflow[https://stackoverflow.com/questions/4459379/preview-an-image-before-it-is-uploaded]
    let output = document.getElementById('recipe-header_image');
    output.classList.remove('hide');
    output.src = URL.createObjectURL(event.target.files[0]);
    output.onload = function () {
        URL.revokeObjectURL(output.src) // free memory
    }
};