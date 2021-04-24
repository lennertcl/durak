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
            case 'finishround':
                on_finish_round(data);
        }
    });

    // Events when other players make a move
    socket.on('move', data => {
        switch(data.event){
            case 'throwcards':
                on_throwcards(data);
            break;
            case 'takecards':
                on_takecards();
            break;
            case 'breakcards':
                on_breakcards(data);
            break;
            case 'breakcard':
                on_breakcard(data);
            break;
            case 'passcards':
                on_passcards(data);
            break;
            case 'passtrump':
                on_passtrump(data);
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

    // When user clicks pass using cards button
    document.querySelector('#passcards').onclick = () => {
        console.log("test");
        passcards();
    }

    // When user clicks pass using cards button
    document.querySelector('#passtrump').onclick = () => {
        passtrump();
    }

    // When user clicks the leave button
    document.querySelector('#leave_button').onclick = () => {
        socket.emit('leave', {'username': username});
    };

    // When user clicks one of their own cards
    own_cards.onclick = (event) => {
        let target = event.target;
        if (!target.id.includes("card")){
            // Don't select the div
            return;
        }
        if (selected_cards.includes(target.id)){
            // Unselect card if already selected
            selected_cards = selected_cards.filter((value, index, arr) => value != target.id);
            target.style.borderColor = '';
            target.style.borderStyle = '';
            target.style.borderWidth = '';
        }else{
            selected_cards.push(target.id);
            target.style.borderColor = 'black';
            target.style.borderStyle = 'solid';
            target.style.borderWidth = 'medium';
        }
    }

    // When user clicks the cards on the table
    table_cards.onclick = (event) => {
        let target = event.target;
        if(target.id == table_cards.id){
            // User throws new cards onto table
            if(current_player != username){
                // Only other players can throw cards
                throwcards();
            }
        }
        else{
            if (selected_cards.length == 1){
                // You can only throw 1 card on top of other card
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
        // Show the cards on the table
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
        if(username != data.player){
            // Edit the player's card count
            var player_count = document.
                getElementById('cardcount' + data.player);
            player_count.innerHTML = parseInt(player_count.innerHTML)
                                        - data.cards.length;
        }
        // TODO animation that cards have been thrown
        // from data.player to table cards
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
    function on_takecards(){
        // Add the number of cards to the taking 
        // player's number of cards
        if(current_player != username){
            // Only if it's another player
            var player_count = document.
                getElementById('cardcount' + current_player);
            var table_card_count = table_cards.
                getElementsByClassName('table-card-pair').length;
            player_count.innerHTML = parseInt(player_count.innerHTML)
                                     + table_card_count;
        }
    }

    // Take cards into hand
    function takecards(){
        var pairs = table_cards.getElementsByClassName('table-card-pair');
        // Prevent the user from pressing take cards before
        // any cards where thrown
        if(pairs.length == 0){
            // TODO message to user
            console.log("No cards to take yet");
            return;
        }
        // Let the other players know
        socket.emit('takecards', {});
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
        // on_finish_round handles everything
        // except cheating?
    }

    // Take cards into hand
    function breakcards(){
        // TODO Ask other players if they want to 
        // throw more cards first
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

    // User passes cards using extra cards
    function passcards(){
        // TODO if no cards?
        socket.emit('passcards', {'cards': selected_cards});
        // Remove the cards from your hand
        for(var i = 0; i < selected_cards.length; i++){
            var card = document.getElementById(selected_cards[i]);
            card.remove();
        }
        // Clear the selected cards
        selected_cards = [];
    }

    // Some player passed using cards
    function on_passcards(data){
        // Add the cards to the table
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
        update_current_player(data.newplayer);
    }

    // User passes cards using his trump card
    function passtrump(){
        socket.emit('passtrump', {});
    }

    // Some player passed using trump
    function on_passtrump(data){
        update_current_player(data.newplayer);
    }

    // Change everything after the round is finished
    function on_finish_round(data){
        // Clear all cards from the table
        table_cards.innerHTML = '';
        // Reload the cards in the player's hand
        for(var i = 0; i < data.cards.length; i++){
            var card_id = "card" + data.cards[i];
            if(!document.getElementById(card_id)) {
                const card = make_card(card_id);
                own_cards.append(card);
            }
        }
        // TODO Set correct player card counts

        // Update card count of deck
        document.getElementById('deckcount').innerHTML = 
            data.deckcount;

        update_current_player(data.newplayer);
    }

    function update_current_player(new_player){
        // If you were the current player
        if (current_player == username){
            on_not_current_player();
        }
        // If you are the new current player:
        else if(new_player == username){
            on_current_player();
        }
        // Update the current player
        current_player = new_player;
        // Set styling for current player
        if (username != current_player){
            // TODO Set styling for current player
        }
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