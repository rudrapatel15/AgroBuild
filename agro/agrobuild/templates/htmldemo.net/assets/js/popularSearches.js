// function showPopularSearches() {
//     document.getElementById('popularSearches').style.display = 'block';
// }

// function hidePopularSearches() {
//     setTimeout(function() {
//         document.getElementById('popularSearches').style.display = 'none';
//     }, 200);
// }
const searchInput = document.getElementById('searchInput');
const popularSearches = document.getElementById('popularSearches');

searchInput.addEventListener('focus', () => {
    popularSearches.style.display = 'block';
});

searchInput.addEventListener('blur', () => {
    setTimeout(() => {
        popularSearches.style.display = 'none';
    }, 200); // Slight delay to allow click events inside the box
});