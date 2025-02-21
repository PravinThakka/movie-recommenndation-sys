function getRecommendations() {
    const movieName = document.getElementById("movieInput").value.trim();
    const resultsDiv = document.getElementById("results");
    
    if (movieName === "") {
        resultsDiv.innerHTML = "<p class='error'>Please enter a movie name.</p>";
        return;
    }

    fetch(`http://127.0.0.1:5000/recommend?movie=${movieName}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultsDiv.innerHTML = `<p class='error'>${data.error}</p>`;
            } else {
                resultsDiv.innerHTML = "<h3>Recommended Movies:</h3><ul>";
                resultsDiv.innerHTML += '<div id="movie-list"></div>';
                const movieListDiv = document.getElementById("movie-list");
                data.recommendations.forEach(movie => {
                    let movieItem = document.createElement("p");
                    movieItem.textContent = `🎬 ${movie}`;
                    movieItem.classList.add("movie-item"); // Apply styling
                    movieListDiv.appendChild(movieItem);
                });
                resultsDiv.innerHTML += "</ul>";
            }
        })
        .catch(error => {
            resultsDiv.innerHTML = "<p class='error'>Error fetching recommendations. Please try again later.</p>";
            console.error("Error:", error);
        });
}