if (window.location.pathname === '/leaderboard') {
  const leaderboardPromise = fetch("/api/leaderboard").then(res => res.json());

  document.addEventListener('DOMContentLoaded', async () => {
    async function loadLeaderboard() {
      const leaderboardElement = document.getElementById("leaderboard");
      const days = 5;

      try {
          const json = await leaderboardPromise;
          const sortedItems = json.sort((a, b) => parseFloat(b.score) - parseFloat(a.score));
          
          let rank = 1;
          for (let i = 0; i < sortedItems.length; i++) {
              const item = sortedItems[i];
              
              const rankNumber = document.createElement('td');
              rankNumber.classList.add("rankNumber");
              rankNumber.innerText = rank;

              const userHandleSpan = document.createElement('td');
              userHandleSpan.classList.add("leaderboardHandle");
              userHandleSpan.innerText = item.userHandle;

              const scoreSpan = document.createElement('span');
              scoreSpan.classList.add("leaderboardScore");
              scoreSpan.innerText = Math.round(parseFloat(item.score) * 100) / 100;

              const rankDiv = document.createElement('tr');
              rankDiv.classList.add("rank");

              rankDiv.appendChild(rankNumber);
              rankDiv.appendChild(userHandleSpan);
              rankDiv.appendChild(scoreSpan);
              
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
