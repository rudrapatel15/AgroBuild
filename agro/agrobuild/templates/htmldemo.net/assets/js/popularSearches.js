const searchInput = document.getElementById('searchInput');
const popularSearches = document.getElementById('popularSearches');

if (searchInput && popularSearches) {
    searchInput.addEventListener('focus', () => {
        popularSearches.style.display = 'block';
    });

    searchInput.addEventListener('blur', () => {
        setTimeout(() => {
            popularSearches.style.display = 'none';
        }, 200); // Slight delay to allow click events inside the box
    });
}