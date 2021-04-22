document.addEventListener('DOMContentLoaded', () => {
    var socket = io();

    // When user connects to the game
    socket.on('connect', () => {
        socket.emit('join', {"username": username});
    });

    // Events when something changes to game status
    socket.on('status', data => {
        switch(data.event){
            case 'joined':
                on_join(data);
            break;
            case 'left':
                on_left(data);
            break;
            case 'startgame':
                on_startgame(data);
            break;
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

    // Some player joins the game
    function on_join(data){
        // Add to the player list
        p = document.getElementById("sideplayer" + data.username);
        if (!p){
            const p = document.createElement('p');
            p.innerHTML = data.username;
            p.id = "sideplayer" + data.username;
            document.querySelector('#players_list').append(p);
        }
    }

    // Some player leaves the game
    function on_left(data){
        // Remove from the player list
        p = document.getElementById("sideplayer" + data.username);
        document.querySelector('#players_list').removeChild(p);
    }

    // When the game starts
    function on_startgame(data){
        window.location.href = game_url;
    }
}) 