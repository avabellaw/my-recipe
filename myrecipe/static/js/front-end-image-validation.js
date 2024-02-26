// Front-end validation of image uploads
document.addEventListener('DOMContentLoaded', function () {
    let imageUploadBtn = document.getElementById("image-upload-btn");

    imageUploadBtn.onchange = function () {
        const fileFormatsAllowed = [".webp", ".jpg", ".jpeg", ".png"];

        let isValid = fileFormatsAllowed.some(format => imageUploadBtn.value.endsWith(format));

        if (isValid) {
            imageUploadBtn.classList.remove("invalid");
            imageUploadBtn.classList.add("valid");
        } else {
            imageUploadBtn.classList.remove("valid");
            imageUploadBtn.classList.add("invalid");
        }
    };
});