document.addEventListener('DOMContentLoaded', function () {

    // Select the form and input elements
    const searchForm = document.getElementById('search-form');
    const roleInput = document.querySelector('input[name="role"]');
    const locationInput = document.querySelector('input[name="location"]');
    const experienceSelect = document.querySelector('select[name="experience"]');

    // Function to validate form inputs
    function validateForm() {
        const roleValue = roleInput.value.trim();
        const locationValue = locationInput.value.trim();
        const experienceValue = experienceSelect.value.trim();

        if (!roleValue) {
            alert("Please enter a job title, keyword, or company.");
            return false;
        }
        if (!locationValue) {
            alert("Please enter a location.");
            return false;
        }
        if (!experienceValue) {
            alert("Please select an experience level.");
            return false;
        }

        return true;
    }

    // Handle form submission
    searchForm.addEventListener('submit', function (event) {
        if (!validateForm()) {
            event.preventDefault(); // Prevent form submission if validation fails
        }
    });

    // Add dynamic behavior: Focus on the next input field when pressing Enter
    [roleInput, locationInput].forEach(input => {
        input.addEventListener('keypress', function (event) {
            if (event.key === 'Enter') {
                event.preventDefault(); // Prevent form submission
                if (this === roleInput) {
                    locationInput.focus(); // Move to the location field
                } else if (this === locationInput) {
                    experienceSelect.focus(); // Move to the experience field
                }
            }
        });
    });

    // Scroll to the job listings after search
    searchForm.addEventListener('submit', function () {
        setTimeout(function () {
            document.querySelector('.jobs').scrollIntoView({ behavior: 'smooth' });
        }, 500); // Adjust delay if necessary
    });

    // Display loader while waiting for job results (you can customize the loader)
    const loader = document.createElement('div');
    loader.classList.add('loader');
    loader.innerHTML = '<p>Loading job listings...</p>';
    document.body.appendChild(loader);

    // Show and hide loader
    searchForm.addEventListener('submit', function () {
        loader.style.display = 'block';
    });
    window.addEventListener('load', function () {
        loader.style.display = 'none';
    });

});