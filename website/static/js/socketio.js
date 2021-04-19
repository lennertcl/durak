document.addEventListener('DOMContentLoaded', () => {
    var socket = io();
    var selected_cards = [];
    var own_cards = document.getElementById('owncards');
    var other_players = null;

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

    // Events when other players make a move
    socket.on('move', data => {
        if (data.event == 'throwcards'){
            // Player throws a card on the table
            console.log(data);

        } else if (data.event == 'takecards'){

        } else if (data.event == 'breakcards'){

        } else if (data.event == 'breakcard'){

        } else if (data.event == 'passcards'){

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

    // TODO do this every time cards are taken into hands
    // When user clicks a card
    own_cards.onclick = (event) => {
        let target = event.target;
        // TODO add some styling to card if selected
        if (selected_cards.includes(target.id)){
            // Unselect card if already selected
            selected_cards.filter((value, index, arr) => value != target.id);
        }else{
            selected_cards.push(target.id);
        }
    }

    // Throw cards into the game
    // Let other players know cards have been thrown
    function throwcards(){
        socket.emit('throwcards', 
            {'username': username,
             'cards': selected_cards});
    }

    // Take cards into hand
    // Let other players know cards have been taken
    function throwcards(){
        socket.emit('takecards', 
            {'username': username});
    }
}) 