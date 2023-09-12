console.log("Leaderboard.js loaded");

function isWithinLastDays(dateString, days) {
  // Parse the input date string into a Date object
  const inputDate = new Date(dateString);

  // Get the current date
  const currentDate = new Date();

  // Calculate the time difference in milliseconds
  const timeDifference = currentDate - inputDate;

  // Calculate the number of milliseconds in 7 days
  const sevenDaysInMilliseconds = days * 24 * 60 * 60 * 1000;

  // Check if the time difference is less than 7 days
  return timeDifference <= sevenDaysInMilliseconds;
}

async function loadLeaderboard() {
  // Get leaderboard div
  const leaderboardElement = document.getElementById("leaderboard");

  const res = await fetch("/api/search");
  const json = await res.json();
  let userData = {};
  for (let i = 0; i < json.length; i++) {
    const flit = json[i];
    const handle = flit["userHandle"];
    console.log(flit);
    if (flit['is_reflit'] == 1) {
      continue;
    }
    if (userData[handle] != undefined) {
      userData[handle]++;
    } else {
      userData[handle] = 1;
    }
    if (!isWithinLastDays(flit["timestamp"], 30)) {
      break;
    }
  }
  const sortedUserData = Object.entries(userData).sort((a, b) => b[1] - a[1]);
  console.log(sortedUserData);
  for (let i = 0; i < sortedUserData.length; i++) {
    const singleUserData = {
      "handle": sortedUserData[i][0],
      "flits": sortedUserData[i][1],
    };
    console.log(singleUserData);

    // Rank number span declaration
    const rankNumber = document.createElement('td');
    rankNumber.classList.add("rankNumber");
    rankNumber.innerText = i+1;

    // User handle span declaration
    const userHandleSpan = document.createElement('td');
    userHandleSpan.classList.add("leaderboardHandle");
    userHandleSpan.innerText = singleUserData["handle"];

    // Score span declaration
    const score = document.createElement('td');
    score.classList.add("leaderboardScore");
    score.innerText = singleUserData["flits"];

    // Main rank div declaration
    const rank = document.createElement('tr');
    rank.classList.add("rank");
    

    // Add elements to rank div
    rank.appendChild(rankNumber);
    rank.appendChild(userHandleSpan);
    rank.appendChild(score);
    
    // Add rank div to leaderboard
    leaderboardElement.appendChild(rank);
  }
}

loadLeaderboard();