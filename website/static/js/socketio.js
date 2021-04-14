document.addEventListener('DOMContentLoaded', () => {
    var socket = io();

    socket.on('connect', () => {
        socket.send("Connected");
    });

    socket.on('message', data => {
        const p = document.createElement('p');
        p.innerHTML = data.msg;
        document.querySelector('#test_display').append(p);
    });

    socket.on('some-event', data => {
        console.log(data);
    });

    document.querySelector('#test_button').onclick = () => {
        socket.send({'username': username,
                    'msg': document.querySelector('#test_input').value});
    }
})