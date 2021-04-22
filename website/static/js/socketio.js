document.addEventListener('DOMContentLoaded', () => {
    var socket = io();
    var selected_cards = [];
    const own_cards = document.getElementById('owncards');
    const table_cards = document.getElementById('tablecards');
    const current_player_buttons = document.getElementById('currentplayerbuttons');

    // When user leaves the game
    socket.on('connect', () => {
        socket.emit('join', {"username": username});
    });

    // Update player list when players join or leave
    // Redirect when someone clicks start game
    // TODO move to functions on_join_game, on_leave_game, on_start_game
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
            // TODO set information given by startgame event
            // eg currentplayer = data.currentplayer
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
        breakcards();
    }

    // When user clicks the take cards button
    document.querySelector('#takecards').onclick = () => {
        takecards();
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

    // Some player takes cards into his hand
    function on_takecards(data){
        // Add the number of cards to the taking 
        // player's number of cards
        if(data.player != username){
            // Only if it's another player
            var count = document.getElementById('cardcount' + data.player);
            count.innerHTML = parseInt(count.innerHTML)
                            + parseInt(data.cardcount);
        }
        // The round is finished when a player
        // takes the cards
        on_finish_round(data);
    }

    // Take cards into hand
    function takecards(){
        socket.emit('takecards', 
            {'username': username});
    }

    // Some player breaks the cards
    function on_breakcards(data){
        // Nothing else happens
        on_finish_round(data);
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

    // Change everything after the round is finished
    function on_finish_round(data){
        // Clear all cards from the table
        table_cards.innerHTML = '';
        // Reload the cards in the player's hand
        // TODO reload the cards
        selected_cards = [];

        // If you were the current player
        // TODO
        if (false){
            on_current_player();
        }
        // If you are the new current player:
        if(data.newplayer == username){
            on_not_current_player();
        }
    }

    // When this player becomes the current player
    function on_current_player(){
        current_player_buttons.display = "block";
    }

    // When this player stops being the current player
    function on_not_current_player(){
        current_player_buttons.display = "none";
    }
}) 