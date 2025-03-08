console.log("Leaderboard.js loaded");

if (window.location.pathname === '/leaderboard') {
  const leaderboardPromise = fetch("/api/leaderboard").then(res => res.json());

  document.addEventListener('DOMContentLoaded', async () => {
    async function loadLeaderboard() {
      // Get leaderboard div
      const leaderboardElement = document.getElementById("leaderboard");
      
      // Constants
      const days = 5;

      try {
          const json = await leaderboardPromise;
          
          // Sort the leaderboard items
          const sortedItems = json.sort((a, b) => parseFloat(b.score) - parseFloat(a.score));
          
          let rank = 1;
          for (let i = 0; i < sortedItems.length; i++) {
              const item = sortedItems[i];
              
              // Rank number span declaration
              const rankNumber = document.createElement('td');
              rankNumber.classList.add("rankNumber");
              rankNumber.innerText = rank;

              // User handle span declaration
              const userHandleSpan = document.createElement('td');
              userHandleSpan.classList.add("leaderboardHandle");
              userHandleSpan.innerText = item.userHandle;

              // Score span declaration
              const scoreSpan = document.createElement('span');
              scoreSpan.classList.add("leaderboardScore");
              scoreSpan.innerText = Math.round(parseFloat(item.score) * 100) / 100;

              // Main rank div declaration
              const rankDiv = document.createElement('tr');
              rankDiv.classList.add("rank");

              // Add elements to rank div
              rankDiv.appendChild(rankNumber);
              rankDiv.appendChild(userHandleSpan);
              rankDiv.appendChild(scoreSpan);
              
              // Add rank div to leaderboard
              leaderboardElement.appendChild(rankDiv);

              rank++;
          }
      } catch (error) {
          console.error("Error loading leaderboard:", error);
      }
    }

    loadLeaderboard();
  });
}
