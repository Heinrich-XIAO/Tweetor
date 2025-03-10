if (window.location.pathname === '/users') {
    socket.on('online_update', function(online) {
        const userslist = document.getElementById('users-list');
        userslist.innerHTML = '';
        for (const user of Object.keys(online)) {
            const p = document.createElement('p');
            p.textContent = user;
            userslist.appendChild(p);
        }
    });
}