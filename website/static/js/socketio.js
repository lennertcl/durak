document.addEventListener('DOMContentLoaded', () => {
    var socket = io();
    var selected_cards = [];
    var own_cards = document.getElementById('owncards');
    var table_cards = document.getElementById('tablecards');
    var break_cards_button = document.getElementById('breakcards');
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
        switch(data.event){
            case 'throwcards':
                on_throwcards(data);
            break;
            case 'takecards':
                on_takecards(data);
            break;
            case 'breakcards':
                on_breakcards(data);
            break;
            case 'breakcard':
                on_breakcard(data);
            break;
            case 'passcard':
                on_passcard(data);
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

    // When user clicks the break cards button
    document.querySelector('#breakcards').onclick = () => {
        socket.emit('breakcards', {});
    }

    // TODO does this need to be reset every time 
    // cards are taken into hands?
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

    // When user clicks the cards on the table
    table_cards.onclick = (event) => {
        // TODO where should user click to add cards
        let target = event.target;
        if(target.id == table_cards.id){
            // User throws new cards onto table
            throwcards();
        }
        else{
            if (selected_cards.length > 1){
                // You can only throw 1 card on top of other card
                // TODO Show error message to user
            }
            else{
                // User throws new card onto other cards
                breakcard(target.id);
            }
        }

    }
    
    // Some player throws cards on the table
    function on_throwcards(data){
        for(var i = 0; i < data.cards.length; i++){
            const card = document.createElement('img');
            card.src = image_dir + data.cards[i].replace("card", "") + ".png";
            card.className = "card";
            table_cards.append(card);
        }
        // TODO animation that cards have been thrown
        // from data.username to table cards
    }

    // Throw cards into the game
    function throwcards(){
        // Let other users know
        socket.emit('throwcards', 
            {'username': username,
             'cards': selected_cards});
        // Remove the cards from your hand
        for(var i = 0; i < selected_cards.length; i++){
            var card = document.getElementById(selected_cards[i]);
            card.remove();
        }
        // Clear the selected cards
        selected_cards = [];
    }

    // Take cards into hand
    function takecards(){
        socket.emit('takecards', 
            {'username': username});
    }

    // Some player breaks the cards
    function on_breakcards(data){
        // Clear all cards from the table
        table_cards.innerHTML = '';
    }

    // Take cards into hand
    function breakcards(){
        socket.emit('breakcards', 
            {'username': username});
    }

    // Some player breaks a card
    function on_breakcard(data){
        // TODO put data.topcard on top of data.bottomcard
    }

    // Break a card: put another card on top of it
    // This can only be called when you only have
    // one selected card
    function breakcard(bottom_card){
        socket.emit('breakcard',
            {'username': username,
             'bottomcard': bottom_card,
             'topcard': selected_cards[0]});
        // Remove the card from your hand
        document.getElementById(selected_cards[0]).remove();
        // Clear the selected cards
        selected_cards = [];
    }
}) 