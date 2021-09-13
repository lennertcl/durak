document.addEventListener('DOMContentLoaded', () => 
{
    var socket = io();
    var selectedCards = [];
    var selectedTopCard = null;

    const ownCards = document.getElementById('owncards');
    const tableCards = document.getElementById('tablecards');
    const currentPlayerButtons = document.getElementById('currentplayerbuttons');
    const allowBreakButton = document.getElementById('allowbreakbutton');

    // Execute once when loading the page
    onStartGame();


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
                onJoin(data);
            break;
            case 'left':
                onLeft(data);
            break;
            case 'finishround':
                onFinishRound(data);
            break;
            case 'startgame':
                location.reload();
            break;
            case 'chat':
                onChat(data)
            break;
        }
    });

    socket.on('move', data => 
    {
        switch(data.event)
        {
            case 'throwcards':
                onThrowCards(data);
            break;
            case 'takecards':
                onTakeCards();
            break;
            case 'breakcards':
                onBreakCards(data);
            break;
            case 'breakcard':
                onBreakCard(data);
            break;
            case 'passcards':
                onPassCards(data);
            break;
            case 'passtrump':
                onPassTrump(data);
            break;
            case 'movetopcard':
                onMoveTopCard(data);
            break;
            case 'allowbreak':
                onAllowBreak(data);
            break;
        }
    });

    socket.on('cheat', data =>
    {
        switch(data.event)
        {
            case 'stealtrump':
                onStealTrumpCard(data);
            break;
            case 'putintodeck':
                onPutIntoDeck(data);
            break;
            case 'callcheat':
                onCallCheat(data);
            break;
        }
    });
    

    // BUTTON EVENTS


    document.querySelector('#takecards').onclick = takeCards;
    
    document.querySelector('#breakcards').onclick = tryBreakCards;

    document.querySelector('#passcards').onclick = tryPassCards;

    document.querySelector('#passtrump').onclick = tryPassTrump;

    document.querySelector('#allowbreakbutton').onclick = allowBreakCards;

    document.querySelector('#leave_button').onclick = () => 
    {
        socket.emit('leave', {'username': username});
    };

    document.querySelector('#start_button').onclick = () => 
    {
        socket.emit('startgame', {})
    }

    document.querySelector('#chat_button').onclick = toggleChatOptions;

    document.querySelector('#chat_options').onclick = onChatOptionsClick;

    var otherPlayers = document.getElementById('otherplayers').children;
    for (var i = 0; i < otherPlayers.length; i++)
    {
        var cheater = otherPlayers[i].id.replace('player', '');
        otherPlayers[i].onclick = () => { tryCallCheat(cheater); }
    }


    // CARD EVENTS


    document.addEventListener("dragover", event => 
    {
        // Prevent default to make sure drop events work as expected
        event.preventDefault();
    });

    ownCards.addEventListener('click', onOwnCardsClick);

    ownCards.addEventListener('dragstart', onOwnCardsDrag);

    tableCards.addEventListener('click', onTableCardsClick);

    tableCards.addEventListener('dragstart', onTableCardsDrag);

    tableCards.addEventListener('drop', onTableCardsClick);

    document.getElementById('deck').addEventListener('click', tryPutIntoDeck);
    document.getElementById('deck').addEventListener('drop', tryPutIntoDeck);

    document.getElementById('trumpcard').addEventListener('click', tryStealTrumpCard);
    document.getElementById('trumpcard').addEventListener('drop', tryStealTrumpCard);


    // GAME STATUS


    function onStartGame()
    {
        updateCurrentPlayer(currentPlayer);
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
    function onJoin(data)
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
    function onLeft(data)
    {
        var p = document.getElementById("sideplayer" + data.username);
        p.remove();

        p = document.getElementById("player" + data.username);
        if (p)
        {
            p.remove();
        }
    }

    /**
     * Display a chat message popup
     * 
     * @param {object} data 
     *      Object containing data about chat event
     *      {
     *          'event': 'chat',
     *          'content': <content of the message sent>,
     *          'player': <username of the player sending the chat> 
     *      }
     * 
     * A popup is displayed at the player's position 
     */
    function onChat(data)
    {
        if (data.player != username)
        {
            document.getElementById("chat" + data.player).innerText = data.content;
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
    function onOwnCardsClick(event)
    {
        let card = event.target.id;

        if (!card.includes('card'))
        {
            return;
        }

        if (selectedCards.includes(card))
        {
            unselectCard(card);
        }
        else
        {
            selectCard(card);
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
    function onTableCardsClick(event)
    {
        // Prevent reloading
        event.preventDefault();

        let target = event.target;

        // User throws new cards onto table
        if(target.id == tableCards.id)
        {
            // Only other players can throw cards
            if(currentPlayer != username)
            {
                tryThrowCards();
            }
        }
        else
        {
            onTableCardClick(target);
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
    function onTableCardClick(target)
    {
        // You can only throw 1 card on top of other card
        if (selectedCards.length == 1)
        {
            breakcard(target.id);
        }
        // Current player can move top cards
        else if (currentPlayer == username)
        {
            if (target.className.includes('bottom-card') && selectedTopCard)
            {
                moveTopCard(target.id);
            }
            else if (target.className.includes('top-card'))
            {
                selectOrUnselectTopCard(target.id);
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
    function onOwnCardsDrag(event)
    {
        var card = event.target;
        if (card.id.includes('card'))
        {
            selectCard(card.id);
        }
    }

    /**
     * Event when a user drags starting from the table cards
     * 
     * @param {*} event 
     *      The ondrag event 
     */
    function onTableCardsDrag(event)
    {
        target = event.target;
        if (username == currentPlayer && target.className.includes('top-card'))
        {
            unselectTopCard();
            selectTopCard(target.id);
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
    function selectCard(card)
    {
        if (selectedCards.includes(card))
        {
            return;
        }

        selectedCards.push(card);
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
    function unselectCard(card)
    {
        if (!selectedCards.includes(card))
        {
            return;
        }

        selectedCards = selectedCards.filter((value) => value != card);
        document.getElementById(card).classList.remove('selected-card');
    }

    /**
     * If the card was currently the top card, unselect it
     * Otherwise, make the clicked card the top card
     * 
     * @param {string} clicked_card 
     *      ID of the card
     */
    function selectOrUnselectTopCard(clicked_card)
    {
        if(selectedTopCard == clicked_card)
        {
            unselectTopCard();
        }
        else if(!selectedTopCard)
        {
            selectTopCard(clicked_card);
        }
    }
    
    /**
     * @param {string} cardToSelect
     *      ID of the card to select
     */
    function selectTopCard(cardToSelect)
    {
        selectedTopCard = cardToSelect;

        const card = document.getElementById(selectedTopCard);
        card.classList.add('selected-card');
    }

    function unselectTopCard()
    {
        const card = document.getElementById(selectedTopCard);
        if (card) 
        {
            card.classList.remove('selected-card');
        }
        selectedTopCard = null;
    }


    // THROWING CARDS


    /**
     * Try throwing the currently selected cards onto the table
     * 
     * A throwcards event is emitted to the backend
     */
    function tryThrowCards()
    {
        socket.emit('throwcards', {'username': username, 
                                   'cards': selectedCards});
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
    function onThrowCards(data)
    {
        if (username == data.player)
        {
            doThrowCards();
        }
        else
        {
            var playerCount = document.getElementById('cardcount' + data.player);
            playerCount.innerHTML = parseInt(playerCount.innerHTML) - data.cards.length;

            animateCardMovement(data.cards[0],
                                document.getElementById('player' + data.player),
                                tableCards);
        }

        for(var i = 0; i < data.cards.length; i++)
        {
            // Create a new bottom-top card pair
            const pair = document.createElement('div');
            pair.className = "table-card-pair";
            // Set the bottom card to the thrown card
            const card = makeCard(data.cards[i]);
            card.className = "card bottom-card";
            pair.append(card);
            tableCards.append(pair);
        }
    }

    /**
     * Throw cards into the game
     * 
     * The cards are removed from your hand
     * Your selected cards are cleared
     */
    function doThrowCards()
    {
        animateCardMovement(selectedCards[0], ownCards, tableCards);

        for(var i = 0; i < selectedCards.length; i++)
        {
            var card = document.getElementById(selectedCards[i]);
            card.remove();
        }

        selectedCards = [];
    }


    // TAKING CARDS


    /**
     * Take cards into the hands of the taking player
     * 
     * If the player taking the cards is not this player, the number of cards is
     * added to the taking player's number of cards.
     */
    function onTakeCards()
    {
        if(currentPlayer != username)
        {
            var playerCount = document.getElementById('cardcount' + currentPlayer);
            var tableCardCount = tableCards.getElementsByClassName('table-card-pair').length;

            playerCount.innerHTML = parseInt(playerCount.innerHTML) + tableCardCount;

            animateCardMovement('', tableCards, document.getElementById('player' + currentPlayer), true);
        }
    }

    /**
     * Take cards into this player's hands
     * 
     * The user is prevented from taking cards before any cards were thrown.
     * The event is emitted to the server.
     * The cards are taken into the user's hands: both bottom and top cards are
     * taken from the table and put into the user's hands.
     */
    function takeCards()
    {
        var pairs = tableCards.getElementsByClassName('table-card-pair');

        if(pairs.length == 0)
        {
            return;
        }

        socket.emit('takecards', {});

        for(var i = 0; i < pairs.length; i++)
        {
            var cards = pairs[i].getElementsByTagName('img');
            const bottomCard = makeCard(cards[0].id);
            ownCards.append(bottomCard);

            if (cards.length == 2)
            {
                const topCard = makeCard(cards[1].id);
                ownCards.append(topCard);
            }
        }

        animateCardMovement('', tableCards, ownCards, true);
    }


    // BREAKING CARDS


    /**
     * Another player breaks the cards 
     * 
     * @param {object} data 
     *      The event data
     * 
     * For now everything is handled by onFinishRound, but this will probably
     * change when cheating is implemented
     */
    function onBreakCards(data)
    {
    }

    function tryBreakCards()
    {
        socket.emit('breakcards', {'username': username});
    }

    /**
     * Make another user break a card
     *  
     * @param {object} data 
     *      Object containing data about the break card event
     *      {
     *          'event': 'breakcard',
     *          'bottomcard': <id of the card getting broken>,
     *          'topcard': <id of the card used to break>,
     *          'player': <username of the player breaking the card>
     *      }
     * 
     * If the player breaking the card is this user, the card is removed
     * from the user's hand and the selected cards are cleared.
     * Otherwise, the amount of cards of the breaking player is updated.
     * The top card is displayed on top of the bottom card of the table.
     */
    function onBreakCard(data)
    {
        if(data.player == username)
        {
            document.getElementById(selectedCards[0]).remove();
            selectedCards = [];
            animateCardMovement(data.topcard, ownCards, tableCards);
        }
        else
        {
            var playerCount = document.getElementById('cardcount' + currentPlayer);
            playerCount.innerHTML = parseInt(playerCount.innerHTML) - 1;
            animateCardMovement(data.topcard, 
                                document.getElementById('player' + data.player),
                                tableCards);
        }

        var pair = document.getElementById(data.bottomcard).parentElement;
        const card = makeCard(data.topcard);
        card.className = "card top-card";
        pair.append(card);
    }

    /**
     * @param {string} bottomCard 
     *      Id of the card that is getting broken
     */
    function breakcard(bottomCard)
    {
        socket.emit('breakcard', {'username': username,
                                  'bottomcard': bottomCard,
                                  'topcard': selectedCards[0]});
    }

    /**
     * @param {object} data 
     *      Object containing information about the allow break event
     *      {
     *          'event': 'allowbreak',
     *          'player': <username of the player allowing the break>
     *      }
     */
    function onAllowBreak(data)
    {
        if(data.player != username)
        {
            const player = document.getElementById('player' + data.player);
            player.classList.add('allowed-break-player');
        }
    }

    function allowBreakCards()
    {
        socket.emit('allowbreak', {});
        allowBreakButton.disabled = true;
    }

    /**
     * Move a top card
     * 
     * @param {object} data 
     *      Object containing information about the move top card event
     *      {
     *          'event': 'movetopcard',
     *          'new_bottomcard': <id of the destination bottom card>,
     *          'topcard': <id of the top card getting moved> 
     *      }
     * 
     * The old top card is removed and a new top card is put on top of the
     * given destination bottom card.
     */
    function onMoveTopCard(data)
    {
        document.getElementById(data.topcard).remove();

        var pair = document.getElementById(data.new_bottomcard).parentElement;
        const card = makeCard(data.topcard);
        card.className = "card top-card";
        pair.append(card);
    }

    /**
     * @param {string} newBottomCard 
     *      Id of the destination bottom card
     */
    function moveTopCard(newBottomCard)
    {
        socket.emit('movetopcard', {'new_bottomcard': newBottomCard,
                                    'topcard': selectedTopCard});
        unselectTopCard();
    }


    // PASSING CARDS


    function tryPassCards()
    {
        socket.emit('passcards', {'cards': selectedCards});
    }

    /**
     * Pass cards on the table
     * 
     * @param {object} data 
     *      Object containing information about the pass cards event
     *      {
     *          'event': 'passcards', 
     *          'player': <username of the player passing the cards>,
     *          'newplayer': <username of the new current player>,
     *          'cards': <list of ids of cards getting passed>
     *      }
     * 
     * If the player passing the cards is the user, pass the cards.
     * Otherwise, edit the amount of cards the player is passing on.
     * Add the cards to the table.
     * Update the current player.
     */
    function onPassCards(data)
    {
        var amount = data.cards.length;
        if (data.player == username)
        {
            doPassCards();
        }
        else
        {
            var playerCount = document.getElementById('cardcount' + currentPlayer);
            playerCount.innerHTML = parseInt(playerCount.innerHTML) - amount;
        }

        for(var i = 0; i < amount; i++)
        {
            const pair = document.createElement('div');
            pair.className = "table-card-pair";

            const card = makeCard(data.cards[i]);
            card.className = "card bottom-card";
            pair.append(card);
            tableCards.append(pair);
        }

        updateCurrentPlayer(data.newplayer);
    }

    /**
     * Let this user pass cards with cards of his own hand
     * 
     * The cards are removed from your hand and the selected cards are cleared.
     */
    function doPassCards()
    {
        for(var i = 0; i < selectedCards.length; i++)
        {
            var card = document.getElementById(selectedCards[i]);
            card.remove();
        }

        selectedCards = [];
    }
    
    function tryPassTrump()
    {
        socket.emit('passtrump', {});
    }

    /**
     * @param {object} data 
     *      Object containing information about the pass trump event
     *      {
     *          'event': 'passtrump',
     *          'newplayer': <username of the new current player>
     *      }
     */
    function onPassTrump(data)
    {
        updateCurrentPlayer(data.newplayer);
    }


    // CHEATING
    // STEAL TRUMP CARD


    /**
     * Let this user replace the trump card with another card
     * 
     * @param {string} cardId 
     *      ID of the card to replace the trump card with
     * 
     * The card is removed from your hand.
     * Your selected cards are cleared.
     * The stolen trump card is added to your hand.
     */
    function doStealTrumpCard(cardId)
    {
        var card = document.getElementById(cardId);
        card.remove();

        selectedCards = [];

        animateCardMovement(cardId, 
                            document.getElementById('owncards'),
                            document.getElementById('trumpcard'));

        var oldCardSrc = document.getElementById('trumpcard').src;
        var cardId = 'card' + oldCardSrc.split('/').splice(-1)[0].split('.')[0];
        ownCards.append(makeCard(cardId));
    }

    function tryStealTrumpCard()
    {
        if (selectedCards.length == 1)
        {
            socket.emit('stealtrump', {card: selectedCards[0]});
        }
    }

    /**
     * @param {object} data 
     *      Object containing information about the steal trump event
     *      {
     *          'event': 'stealtrump',
     *          'player': <username of the player stealing the trump card>
     *          'card': <id of the card it was replaced with>
     *      }
     */
    function onStealTrumpCard(data)
    {
        if (data.player == username)
        {
            doStealTrumpCard(data.card);
        }
        else
        {
            animateCardMovement(data.card, 
                                document.getElementById('player' + data.player),
                                document.getElementById('trumpcard'));
        }

        var newTrumpCardSrc = imageDir + data.card.replace('card', '') + '.png';
        document.getElementById('trumpcard').src = newTrumpCardSrc;
    }


    // PUTTING CARDS INTO DECK


    /**
     * @param {Array<string>} cards 
     *      List of ids of cards getting put into the deck
     */
    function doPutIntoDeck(cards)
    {
        for (var i = 0; i < cards.length; i++)
        {
            document.getElementById(cards[i]).remove();
        }

        selectedCards = [];

        animateCardMovement(cards[0],
                            document.getElementById('owncards'),
                            document.getElementById('deck'));
    }

    function tryPutIntoDeck()
    {
        socket.emit('putintodeck', {cards: selectedCards})
    }

    /**
     * @param {object} data 
     *      Object containing information about the put into deck event
     *      {
     *          'event': 'putintodeck',
     *          'player': <username of the player putting cards into the deck>
     *          'cards': <list of ids of the cards put into the deck>
     *      }
     * 
     * If this user is putting cards into the deck, the put into deck action is
     * performed.
     * Cards are animated from the player to the deck.
     * The deck count is updated.
     */
    function onPutIntoDeck(data)
    {
        if (data.player == username)
        {
            doPutIntoDeck(data.cards);
        }
        else
        {
            animateCardMovement(data.cards[0],
                                document.getElementById('player' + data.player),
                                document.getElementById('deck'));
        }

        var deckCount = document.getElementById('deckcount');
        deckCount.innerHTML = parseInt(deckCount.innerHTML) + data.cards.length;
    }

    function revertDoPutIntoDeck(data)
    {

    }

    function revertPutIntoDeck(data)
    {
        if (data.player == username)
        {
            revertDoPutIntoDeck(data);
        }

    }


    // CALLING OUT CHEATERS


    function tryCallCheat(cheater)
    {
        socket.emit('callcheat', {'cheater': cheater});
    }

    /**
     * @param {object} data 
     *      Object containing information about the call cheat event
     *      {
     *          'event': 'callcheat',
     *          'player': <username of the player calling out the cheater>,
     *          'cheater': <username of the player getting called out>,
     *          'revert': <bool indicating whether the cheat should be reverted>
     *      }
     */
    function onCallCheat(data)
    {
        if (data.revert)
        {
            onRevertCheat(data);
        }

        messageData = { 'event': 'chat',
                        'content': data.cheater + ' cheated!',
                        'player': data.player };
        onChat(messageData)
    }

    /**
     * @param {object} data 
     *      Object containing information about the call cheat event
     *      {
     *          'event': 'callcheat',
     *          'player': <username of the player calling out the cheater>,
     *          'cheater': <username of the player getting called out>,
     *          'revert': true
     *      }
     */
    function onRevertCheat(data)
    {
        // TODO check type of cheat and revert this type
    }


    // HELPER FUNCTIONS


    /**
     * Update everything when the round is finished
     *  
     * @param {object} data 
     *      Object containing information about the finish round event
     *      {
     *          'event': 'finishround',
     *          'newplayer': <username of the new current player>,
     *          'deckcount': <new number of cards in the deck>,
     *          'cardcounts': <new number of cards in each players hand>
     *      }
     * 
     * All cards are cleared from the table.
     * If the player is not a spectator, update the cards in the user's hand.
     * Update the other players: 
     *     If they are still in the game, their card count is updated and if 
     *     they allowed break, they don't allow break anymore.
     *     Otherwise, they are removed from the game.
     * The card count of the deck is updated.
     * The current player is updated.
     * If the user is not playing the game anymore, the buttons only for players
     * are removed.
     */
    function onFinishRound(data)
    {
        tableCards.innerHTML = '';

        if(data.cards)
        {
            for(var i = 0; i < data.cards.length; i++)
            {
                var cardId = "card" + data.cards[i];
                if(!document.getElementById(cardId)) 
                {
                    const card = makeCard(cardId);
                    ownCards.append(card);
                }
            }
        }

        var otherPlayers = document.getElementById('otherplayers').
            getElementsByTagName('div');
        for(var i = 0; i < otherPlayers.length; i++)
        {
            var name = otherPlayers[i].id.replace('player', '');

            if(data.cardcounts[name])
            {
                var count = document.getElementById('cardcount' + name);
                count.innerHTML = data.cardcounts[name];

                if(otherPlayers[i].classList.contains('allowed-break-player'))
                {
                    otherPlayers[i].classList.remove('allowed-break-player');
                }
            }
            else
            {
                var player = document.getElementById('player' + name);
                player.classList.add('finished-player');
            }
        }

        document.getElementById('deckcount').innerHTML = 
            data.deckcount;

        updateCurrentPlayer(data.newplayer);

        if (!data.cardcounts[username])
        {
            var onlyPlayers = document.getElementById('onlyplayers');
            if(onlyPlayers)
            {
                onlyPlayers.remove();
            }
        }
    }


    /**
     * @param {string} newPlayer 
     *      Username of the new current player
     * 
     * If the user was the current player, and he is not the new current player,
     * he is updated to not be the current player anymore.
     * Otherwise, if the user is the new current player, he is updated to be the
     * current player.
     * Styling is removed from the previous current player.
     * Styling is added to the new current player.
     * The current player variable is updated.
     * The allow break button is reset.
     */
    function updateCurrentPlayer(newPlayer)
    {
        if (currentPlayer == username && newPlayer != username)
        {
            onNotCurrentPlayer();
        }
        else if(newPlayer == username)
        {
            onCurrentPlayer();
        }

        var player = document.getElementById('player' + currentPlayer);
        if(player)
        {
            player.className = player.className.replace(' current-player', '');
        }

        player = document.getElementById('player' + newPlayer);
        if(player)
        {
            player.className += ' current-player';
        }

        currentPlayer = newPlayer;

        allowBreakButton.disabled = false;
    }

    function onCurrentPlayer()
    {
        currentPlayerButtons.style.display = 'block';
        allowBreakButton.style.display = 'none';
    }

    function onNotCurrentPlayer()
    {
        currentPlayerButtons.style.display = 'none';
        allowBreakButton.style.display = 'block';
    }

    /**
     * Create a card element from a given card id
     * 
     * @param {string} cardId 
     *      Id of the card to make the element of
     * @param {bool} setId
     *      Set the id of the card to the correct id, defaults to true
     * @returns element
     *      The created card element
     */
    function makeCard(cardId, setId=true)
    {
        const card = document.createElement('img');
        card.src = imageDir + cardId.replace("card", "") + ".png";
        card.className = "card";
        if (setId)
        {
            card.id = cardId;
        }
        return card;
    }

    /**
     * Opens or closes the chat options menu
     */
    function toggleChatOptions()
    {
        const chatOptions = document.getElementById('chat_options');
        if (chatOptions.className == 'chat-open')
        {
            chatOptions.className = 'chat-closed';
        }
        else
        {
            chatOptions.className = 'chat-open';
        }
    }

    /**
     * Sends a chat message to the server
     *  
     * @param {*} event 
     *      The onclick event
     * 
     * Emits the chat event to the server and closes the chat window
     */
    function onChatOptionsClick(event)
    {
        socket.emit('chat', {'content': event.target.innerText});
        toggleChatOptions();
    }

    /**
     * Animate a card moving from one element to another
     * 
     * @param {String} cardId 
     *      Id of the card getting moved
     * @param {*} fromElement 
     *      Element to start moving from
     * @param {*} toElement 
     *      Element to move to
     * @param {Boolean} hidden
     *      Indicates whether the card is hidden
     */
    function animateCardMovement(cardId, fromElement, toElement, hidden=false)
    {
        function getPosition(element)
        {
            var rect = element.getBoundingClientRect();
            return {x: (rect.left + rect.right) / 2, 
                    y: (rect.bottom + rect.top) / 2};
        }

        const from = getPosition(fromElement);
        const to = getPosition(toElement);
        const numberOfSteps = 100;
        const increaseX = (to.x - from.x) / numberOfSteps;
        const increaseY = (to.y - from.y) / numberOfSteps;

        if (hidden)
        {
            var element = makeCard('red_back', setId=false);
        }
        else
        {
            var element = makeCard(cardId, setId=false);
        }
        element.style.position = 'fixed';
        element.style.transform = 'translate(-50%, -50%)';
        element.style.left = from.x + 'px';
        element.style.top = from.y + 'px';
        document.getElementById('game').append(element);

        var currentStep = 0;
        var id = setInterval(move, 5);
        function move()
        {
            if (currentStep == numberOfSteps)
            {
                clearInterval(id);
                element.remove();
            }

            element.style.left = parseFloat(element.style.left.replace('px', '')) + increaseX + 'px';
            element.style.top = parseFloat(element.style.top.replace('px', '')) + increaseY + 'px';
            currentStep++;
        }
    }
}) 
