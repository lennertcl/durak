document.addEventListener('DOMContentLoaded', () => 
{
    var socket = io();
    var selected_cards = [];
    var selected_top_card = null;

    const own_cards = document.getElementById('owncards');
    const table_cards = document.getElementById('tablecards');
    const current_player_buttons = document.getElementById('currentplayerbuttons');
    const allow_break_button = document.getElementById('allowbreakbutton');

    // Execute once when loading the page
    on_startgame();


    // SOCKETIO EVENTS


    socket.on('connect', () => 
    {
        socket.emit('join', {'username': username});
    });

    socket.on('status', data => 
    {
        switch(data.event)
        {
            case 'joined':
                on_join(data);
            break;
            case 'left':
                on_left(data);
            break;
            case 'finishround':
                on_finish_round(data);
            break;
            case 'startgame':
                location.reload();
            break;
        }
    });

    socket.on('move', data => 
    {
        switch(data.event)
        {
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
            break;
            case 'movetopcard':
                on_move_top_card(data);
            break;
            case 'allowbreak':
                on_allow_break(data);
            break;
        }
    });
    

    // BUTTON EVENTS


    document.querySelector('#takecards').onclick = () => 
    {
        takecards();
    }
    
    document.querySelector('#breakcards').onclick = () =>
    {
        try_breakcards();
    }

    document.querySelector('#passcards').onclick = () => 
    {
        try_passcards();
    }

    document.querySelector('#passtrump').onclick = () => 
    {
        try_passtrump();
    }

    document.querySelector('#allowbreakbutton').onclick = () => 
    {
        allow_breakcards();
    }

    document.querySelector('#leave_button').onclick = () => 
    {
        socket.emit('leave', {'username': username});
    };

    document.querySelector('#start_button').onclick = () => 
    {
        socket.emit('startgame', {})
    }


    // CARD EVENTS


    // Prevent default to make sure drop events work as expected
    document.addEventListener("dragover", event => 
    {
        event.preventDefault();
    });

    own_cards.addEventListener('click', on_own_cards_click);

    own_cards.addEventListener('dragstart', on_own_cards_drag);

    table_cards.addEventListener('click', on_table_cards_click);

    table_cards.addEventListener('dragstart', on_table_cards_drag);

    table_cards.addEventListener('drop', on_table_cards_click);


    // GAME STATUS


    function on_startgame()
    {
        update_current_player(current_player);
    }

    /**
     * Add a player to the game
     *  
     * @param {object} data 
     *      Object containing data about player joining event
     *      {
     *          'event': 'joined',
     *          'username': <username of the player joining>
     *      }
     * 
     * If the player wasn't already in the list of players, the player is added
     * to the list of players
     */
    function on_join(data)
    {
        p = document.getElementById("sideplayer" + data.username);
        if (!p)
        {
            const p = document.createElement('p');
            p.innerHTML = data.username;
            p.id = "sideplayer" + data.username;
            document.querySelector('#players_list').append(p);
        }
    }

    /**
     * Remove a player from the game
     * 
     * @param {object} data 
     *      Object containing data about player leaving event
     *      {
     *          'event': 'left',
     *          'username': <username of the player leaving>
     *      }
     * 
     * The player is removed from the player list
     * If the player was still playing he is removed from the table
     */
    function on_left(data)
    {
        var p = document.getElementById("sideplayer" + data.username);
        p.remove();

        p = document.getElementById("player" + data.username);
        if (p)
        {
            p.remove();
        }
    }


    // ONCLICK EVENTS


    /**
     * When a user clicks on his own cards
     * 
     * @param {*} event 
     *      The onclick event
     * 
     * If the clicked element is actually a card then the card is unselected
     * if it was already selected and selected if it wasn't
     */
    function on_own_cards_click(event)
    {
        let card = event.target.id;

        if (!card.includes('card'))
        {
            return;
        }

        if (selected_cards.includes(card))
        {
            unselect_card(card);
        }
        else
        {
            select_card(card);
        }
    }

    /**
     * When a user clicks on the table cards
     * 
     * @param {*} event 
     *      The onclick event
     * 
     * If the user clicks on the table itself (not on the cards), then cards
     * are thrown on the table if the user is not the current player.
     * Otherwise the player clicked a card on the table.
     */
    function on_table_cards_click(event)
    {
        // Prevent reloading
        event.preventDefault();

        let target = event.target;

        // User throws new cards onto table
        if(target.id == table_cards.id)
        {
            // Only other players can throw cards
            if(current_player != username)
            {
                try_throwcards();
            }
        }
        else
        {
            on_table_card_click(target);
        }
    }

    /**
     * When a user clicks on a card on the table 
     * 
     * @param {*} target
     *      The clicked target on the table
     * 
     * If the player has exactly one card selected, the clicked card is broken.
     * Otherwise, if the user is the current player and he clicks a bottom card
     * while having a top card selected, the selected top card is moved to the
     * new bottom card.
     * Otherwise, if the user is the current player and he clicks a top card,
     * the top card is selected or unselected.
     */
    function on_table_card_click(target)
    {
        // You can only throw 1 card on top of other card
        if (selected_cards.length == 1)
        {
            breakcard(target.id);
        }
        // Current player can move top cards
        else if (current_player == username)
        {
            if (target.className.includes('bottom-card') && selected_top_card)
            {
                move_top_card(target.id);
            }
            else if (target.className.includes('top-card'))
            {
                select_or_unselect_top_card(target.id);
            }
        }
    }


    // ON DRAG EVENTS


    /**
     * Event when a user drags starting from his own cards 
     * 
     * @param {*} event 
     *      The ondrag event
     * 
     * If no cards were selected and the user starts dragging from a card,
     * this card is added to the selected cards
     */
    function on_own_cards_drag(event)
    {
        var card = event.target;
        if (card.id.includes('card'))
        {
            select_card(card.id);
        }
    }

    /**
     * Event when a user drags starting from the table cards
     * 
     * @param {*} event 
     *      The ondrag event 
     */
    function on_table_cards_drag(event)
    {
        target = event.target;
        if (username == current_player && target.className.includes('top-card'))
        {
            unselect_top_card();
            select_top_card(target.id);
        }
    }

    /**
     * Select a card from your own cards 
     * 
     * @param {string} card 
     *      ID of the card to select
     * 
     * If the card is already selected, nothing happens
     * Otherwise the card is added to the selected cards and styling is added
     */
    function select_card(card)
    {
        if (selected_cards.includes(card))
        {
            return;
        }

        selected_cards.push(card);
        document.getElementById(card).classList.add('selected-card');
    }

    /**
     * Unselect a card from your own cards 
     * 
     * @param {string} card 
     *      ID of the card to unselect
     * 
     * If the card is not selected, nothing happens
     * Otherwise the card is removed from the selected cards and styling
     * is removed
     */
    function unselect_card(card)
    {
        if (!selected_cards.includes(card))
        {
            return;
        }

        selected_cards = selected_cards.filter((value) => value != card);
        document.getElementById(card).classList.remove('selected-card');
    }

    /**
     * If the card was currently the top card, unselect it
     * Otherwise, make the clicked card the top card
     * 
     * @param {string} clicked_card 
     *      ID of the card
     */
    function select_or_unselect_top_card(clicked_card)
    {
        // Unselecting the top card
        if(selected_top_card == clicked_card)
        {
            unselect_top_card();
        }
        // Selecting a top card
        else if(!selected_top_card)
        {
            select_top_card(clicked_card);
        }
    }
    
    /**
     * @param {string} card_to_select
     *      ID of the card to select
     */
    function select_top_card(card_to_select)
    {
        selected_top_card = card_to_select;

        const card = document.getElementById(selected_top_card);
        card.classList.add('selected-card');
    }

    function unselect_top_card()
    {
        const card = document.getElementById(selected_top_card);
        if (card) 
        {
            card.classList.remove('selected-card');
        }
        selected_top_card = null;
    }


    // THROWING CARDS


    /**
     * Try throwing the currently selected cards onto the table
     * 
     * A throwcards event is emitted to the backend
     */
    function try_throwcards()
    {
        socket.emit('throwcards', 
            {'username': username,
             'cards': selected_cards});
    }

    /**
     * Event when a player throws some cards onto the table 
     * 
     * @param {object} data 
     *      Object containing data about the throwcards event
     *      {
     *          'event': 'throwcards',
     *          'player': <username of the player throwing the cards>,
     *          'cards': <list of card ids of the thrown cards> 
     *      }
     * 
     * If this player is the player throwing the cards, throw the cards
     * Otherwise, edit the throwing player's card count 
     * Show all thrown cards on the table
     */
    function on_throwcards(data)
    {
        if (username == data.player)
        {
            do_throwcards();
        }
        else
        {
            var player_count = document.
                getElementById('cardcount' + data.player);
            player_count.innerHTML = parseInt(player_count.innerHTML)
                                        - data.cards.length;
        }

        for(var i = 0; i < data.cards.length; i++)
        {
            // Create a new bottom-top card pair
            const pair = document.createElement('div');
            pair.className = "table-card-pair";
            // Set the bottom card to the thrown card
            const card = make_card(data.cards[i]);
            card.className = "card bottom-card";
            pair.append(card);
            table_cards.append(pair);
        }
    }

    /**
     * Throw cards into the game
     * 
     * The cards are removed from your hand
     * Your selected cards are cleared
     */
    function do_throwcards()
    {
        for(var i = 0; i < selected_cards.length; i++)
        {
            var card = document.getElementById(selected_cards[i]);
            card.remove();
        }

        selected_cards = [];
    }


    // TAKING CARDS


    // Some player takes cards into his hand
    function on_takecards()
    {
        // Add the number of cards to the taking 
        // player's number of cards
        if(current_player != username)
        {
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
    function takecards()
    {
        var pairs = table_cards.getElementsByClassName('table-card-pair');
        // Prevent the user from pressing take cards before
        // any cards where thrown
        if(pairs.length == 0)
        {
            return;
        }
        // Let the other players know
        socket.emit('takecards', {});
        // Add the cards to your hand
        for(var i = 0; i < pairs.length; i++)
        {
            // Take bottom and top cards of table
            // Add to your own cards
            var cards = pairs[i].getElementsByTagName('img');
            const bottom_card = make_card(cards[0].id);
            own_cards.append(bottom_card);
            if (cards.length == 2)
            {
                // If there is a top card
                const top_card = make_card(cards[1].id);
                own_cards.append(top_card);
            }
        }
    }


    // BREAKING CARDS


    // Some player breaks the cards
    function on_breakcards(data)
    {
        // on_finish_round handles everything
        // except cheating?
    }

    // Take cards into hand
    function try_breakcards()
    {
        socket.emit('breakcards', 
            {'username': username});
    }

    // Some player breaks a card
    function on_breakcard(data)
    {
        if(data.player == username)
        {
            // Remove the cards from your hand if you
            // threw them
            document.getElementById(selected_cards[0]).remove();
            // Clear the selected cards
            selected_cards = [];
        }
        else
        {
            // Edit the amount of cards of the player breaking
            var player_count = document.
                getElementById('cardcount' + current_player);
            player_count.innerHTML = parseInt(player_count.innerHTML) - 1;
        }
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
    function breakcard(bottom_card)
    {
        socket.emit('breakcard',
            {'username': username,
             'bottomcard': bottom_card,
             'topcard': selected_cards[0]});
    }

    // When a user allows break cards
    function on_allow_break(data)
    {
        if(data.player != username)
        {
            const player = document.getElementById('player' + data.player);
            player.classList.add('allowed-break-player');
        }
    }

    // When a user clicks the allow break cards button
    function allow_breakcards()
    {
        socket.emit('allowbreak', {});
        allow_break_button.disabled = true;
    }

    // When a top card has moved
    function on_move_top_card(data)
    {
        // Remove the old top card
        document.getElementById(data.topcard).remove();
        // Make the top card and put it on the new
        // bottom card
        var pair = document.getElementById(data.new_bottomcard).parentElement;
        const card = make_card(data.topcard);
        card.className = "card top-card";
        pair.append(card);
    }

    // When the current player moves one of the top cards
    // to another top card
    function move_top_card(new_bottom_card)
    {
        socket.emit('movetopcard',
            {'new_bottomcard': new_bottom_card,
             'topcard': selected_top_card});

        unselect_top_card();
    }


    // PASSING CARDS


    // Try passing the cards
    // If passing the cards is possible,
    // the server will emit the event to everyone
    function try_passcards()
    {
        socket.emit('passcards', {'cards': selected_cards});
    }

    // Some player passed using cards
    function on_passcards(data)
    {
        var amount = data.cards.length;
        if (data.player == username)
        {
            do_passcards();
        }
        else
        {
            // Edit the amount of cards of the player passing on
            var player_count = document.
                getElementById('cardcount' + current_player);
            player_count.innerHTML = parseInt(player_count.innerHTML)
                                     - amount;
        }
        // Add the cards to the table
        for(var i = 0; i < amount; i++)
        {
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

    // User passes cards using extra cards
    function do_passcards()
    {
        // Remove the cards from your hand
        for(var i = 0; i < selected_cards.length; i++)
        {
            var card = document.getElementById(selected_cards[i]);
            card.remove();
        }
        // Clear the selected cards
        selected_cards = [];
    }
    
    // Try passing the cards
    // If passing the cards is possible,
    // the server will emit the event to everyon
    function try_passtrump()
    {
        socket.emit('passtrump', {});
    }

    // Some player passed using trump
    function on_passtrump(data)
    {
        update_current_player(data.newplayer);
    }


    // HELPER FUNCTIONS


    // Change everything after the round is finished
    function on_finish_round(data)
    {
        // Clear all cards from the table
        table_cards.innerHTML = '';
        if(data.cards)
        {
            // Reload the cards in the player's hand
            // Only if the player is not a spectator
            for(var i = 0; i < data.cards.length; i++)
            {
                var card_id = "card" + data.cards[i];
                if(!document.getElementById(card_id)) 
                {
                    const card = make_card(card_id);
                    own_cards.append(card);
                }
            }
        }

        // Update other players
        var other_players = document.getElementById('otherplayers').
            getElementsByTagName('div');
        for(var i = 0; i < other_players.length; i++)
        {
            var name = other_players[i].id.replace('player', '');

            if(data.cardcounts[name])
            {
                // The player is still in the game
                // Update the card count
                var count = document.getElementById('cardcount' + name);
                count.innerHTML = data.cardcounts[name];

                // Nobody has allowed breaking at the beginning of a round
                if(other_players[i].classList.contains('allowed-break-player'))
                {
                    other_players[i].classList.remove('allowed-break-player');
                }
            }
            else
            {
                // The player has finished playing
                var player = document.getElementById('player' + name);
                player.classList.add('finished-player');
            }
        }

        // Update card count of deck
        document.getElementById('deckcount').innerHTML = 
            data.deckcount;

        update_current_player(data.newplayer);

        if (!data.cardcounts[username])
        {
            // The buttons get removed for spectators
            var only_players = document.getElementById('onlyplayers');
            if(only_players)
            {
                only_players.remove();
            }
        }
   }

    function update_current_player(new_player)
    {
        // If you were the current player
        if (current_player == username
            && new_player != username)
        {
            // You can be the current player
            // twice in a row
            on_not_current_player();
        }
        else if(new_player == username)
        {
            on_current_player();
        }
        // Remove styling from previous current player
        var player = document.getElementById('player' + current_player);
        if(player)
        {
            // Only if the current player had styling
            player.className = player.className.replace(' current-player', '');
        }
        // Add styling to the current player
        player = document.getElementById('player' + new_player);
        if(player)
        {
            player.className += ' current-player';
        }
        // Update the current player
        current_player = new_player;
        // Reset the allow break button
        allow_break_button.disabled = false;
    }

    // When this player becomes the current player
    function on_current_player()
    {
        current_player_buttons.style.display = 'block';
        allow_break_button.style.display = 'none';
    }

    // When this player stops being the current player
    function on_not_current_player()
    {
        current_player_buttons.style.display = 'none';
        allow_break_button.style.display = 'block';
    }

    // Create a card
    function make_card(card_id)
    {
        const card = document.createElement('img');
        card.src = image_dir + card_id.replace("card", "") + ".png";
        card.id = card_id;
        card.className = "card";
        return card;
    }
}) 
