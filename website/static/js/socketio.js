document.addEventListener('DOMContentLoaded', () => {
    var socket = io();

    // When user leaves the game
    socket.on('connect', () => {
        socket.emit('join', {"username": username});
    });

    // Update player list when players join or leave
    // Redirect when someone clicks start game
    socket.on('status', data => {
        if (data.event == 'joined'){
            p = document.getElementById("player" + data.username);
            if (!p){
                const p = document.createElement('p');
                p.innerHTML = data.username;
                p.id = "player" + data.username;
                document.querySelector('#players_list').append(p);
            }
        }
        else if (data.event == 'left'){
            p = document.getElementById("player" + data.username);
            document.querySelector('#players_list').removeChild(p);
        }
        else if (data.event == 'startgame'){
            window.location.href = game_url;
        }
    });
    
    // When user clicks the start game button
    document.querySelector('#start_button').onclick = () => {
        socket.emit('startgame', {});
    };

    // When user clicks the leave button
    document.querySelector('#leave_button').onclick = () => {
        socket.emit('leave', {'username': username});
    };
}) 