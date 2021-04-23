document.addEventListener('DOMContentLoaded', () => {
    var socket = io();
    var selected_cards = [];
    const own_cards = document.getElementById('owncards');
    const table_cards = document.getElementById('tablecards');
    const current_player_buttons = document.getElementById('currentplayerbuttons');
    // Execute once on startup
    on_startgame();


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
    
    // When user clicks take cards button
    document.querySelector('#takecards').onclick = () => {
        takecards();
    }
    
    // When user clicks break cards button
    document.querySelector('#breakcards').onclick = () => {
        breakcards();
    }

    // When user clicks the leave button
    document.querySelector('#leave_button').onclick = () => {
        socket.emit('leave', {'username': username});
    };

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
        if(target.id == table_cards.id && current_player != username){
            // User throws new cards onto table
            // Only if the user is not the current player
            throwcards();
        }
        else{
            if (selected_cards.length == 1){
                // You can only throw 1 card on top of other card
                // TODO if the player is not the current player he cheated
                breakcard(target.id);
            }
            else{
                // TODO Show error message to user
                console.log("No cards / more than 1 card selected when breaking");
            }
        }

    }

    // When the game starts
    function on_startgame(){
        if (current_player == username){
            on_current_player();
        }
    }

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
        // TODO remove from the table
    }

    // Some player throws cards on the table
    function on_throwcards(data){
        for(var i = 0; i < data.cards.length; i++){
            // Create a new bottom-top card pair
            const pair = document.createElement('div');
            pair.className = "table-card-pair";
            // Set the bottom card to the thrown card
            const card = make_card(data.cards[i]);
            card.className = "card bottom-card";
            pair.append(card);
            table_cards.append(pair);
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
        // Let the other players know
        socket.emit('takecards', 
            {'username': username});
        
        var pairs = table_cards.getElementsByClassName('table-card-pair');
        // Add the cards to your hand
        for(var i = 0; i < pairs.length; i++){
            // Take bottom and top cards of table
            // Add to your own cards
            var cards = pairs[i].getElementsByTagName('img');
            const bottom_card = make_card(cards[0].id);
            own_cards.append(bottom_card);
            if (cards.length == 2){
                // If there is a top card
                const top_card = make_card(cards[1].id);
                own_cards.append(top_card);
            }
        }
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
        // Get the bottom card on the table
        var pair = document.getElementById(data.bottomcard).parentElement;
        // Make the top card and put it on the table
        const card = make_card(data.topcard);
        card.className = "card top-card";
        pair.append(card);
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
        selected_cards = [];

        // TODO reload the cards
        // TODO update card count of deck

        // If you were the current player
        if (current_player == username){
            on_not_current_player();
        }
        // If you are the new current player:
        else if(data.newplayer == username){
            on_current_player();
        }

        // Update the current player
        current_player = data.newplayer;
        // Set styling for current player
    }

    // When this player becomes the current player
    function on_current_player(){
        current_player_buttons.style.display = "block";
    }

    // When this player stops being the current player
    function on_not_current_player(){
        current_player_buttons.style.display = "none";
    }

    // Create a card
    function make_card(card_id){
        const card = document.createElement('img');
        card.src = image_dir + card_id.replace("card", "") + ".png";
        card.id = card_id;
        card.className = "card";
        return card;
    }
}) 