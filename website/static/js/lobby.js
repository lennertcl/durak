document.addEventListener('DOMContentLoaded', () => 
{
    var socket = io();


    // SOCKETIO EVENTS 


    socket.on('connect', () => 
    {
        socket.emit('join', {"username": username});
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
            case 'startgame':
                on_startgame(data);
            break;
            case 'message':
                on_message(data)
            break;
        }
    });
    

    // BUTTON EVENTS


    document.querySelector('#start_button').onclick = () => 
    {
        socket.emit('startgame', {});
    };

    document.querySelector('#leave_button').onclick = () => 
    {
        socket.emit('leave', {'username': username});
    };


    // HELPER FUNCTIONS


    /**
     * Add a player to the lobby
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
     * Remove a player from the lobby 
     * 
     * @param {object} data 
     *      Object containing data about player leaving event
     *      {
     *          'event': 'left',
     *          'username': <username of the player leaving>
     *      }
     */
    function on_left(data)
    {
        p = document.getElementById("sideplayer" + data.username);
        document.querySelector('#players_list').removeChild(p);
    }

    function on_startgame()
    {
        window.location.href = game_url;
    }

    /**
     * Create a new flashed message
     *  
     * @param {object} data 
     *      Object containing message data
     *      {
     *          'event': 'message',
     *          'body': <body string of the message>,
     *          'type': <type of bootstrap alert (e.g. danger, info)>
     *      }
     */
    function on_message(data)
    {
        messages = document.getElementById("flashed-messages");
        const message = document.createElement("div");
        message.className = "alert alert-" + data.type;
        message.innerText = data.body;
        messages.append(message);
    }
}) 
