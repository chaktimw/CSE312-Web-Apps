// Establish a WebSocket connection with the server
const socket = new WebSocket('ws://' + window.location.host + '/websocket');

// Call the addMessage function whenever data is received from the server over the WebSocket
socket.onmessage = alertUser;

// // Allow users to send messages by pressing enter instead of clicking the Send button
// document.addEventListener("keypress", function (event) {
//     if (event.code === "Enter") {
//         sendMessage();
//     }
// });

// Read the username/password and send it to the server over the WebSocket as a JSON string
// Called whenever the user clicks the login button
function login() {
    const chatName = (document.getElementById("username").value).replace(/\"/g, "").replace(/\}/g, "");
    const chatBox = document.getElementById("password");
    const comment = (chatBox.value).replace(/\"/g, "").replace(/\}/g, "");
    chatBox.value = "";
    if(comment !== "" && chatName !== "") {
        socket.send(JSON.stringify({'type': 'login', 'username': chatName, 'password': comment}));
    }
}

function register() {
    const chatName = (document.getElementById("username2").value).replace(/\"/g, "").replace(/\}/g, "");
    const chatBox = document.getElementById("password2");
    const comment = (chatBox.value).replace(/\"/g, "").replace(/\}/g, "");
    chatBox.value = "";
    if(comment !== "" && chatName !== "") {
        socket.send(JSON.stringify({'type': 'register', 'username': chatName, 'password': comment}));
    }
}
// // Called when the server sends a new message over the WebSocket and renders that message so the user can read it
// function addMessage(message) {
//     const chatMessage = JSON.parse(message.data);
//     let chat = document.getElementById('chat');
//     chat.innerHTML += "<b>" + chatMessage['username'] + "</b>: " + chatMessage["comment"] + "<br/>";
// }

// Called when server finishes login/register request
function alertUser(message) {
    const data = JSON.parse(message.data);
    const alert = data['alert']
    let registerChat = document.getElementById('register');
    let loginChat = document.getElementById('login');
    let authenticate = document.getElementById('authenticate');
    document.getElementById('welcome').innerHTML = "<h3>Welcome Back!</h3>"

    if (alert === '0') {
        registerChat.innerHTML = "<br><b>Registration Failed: Username already exists.</b>";
    } else if (alert === '1') {
        registerChat.innerHTML = "<br><b>Registration Success!</b>";
    } else if (alert === '2') {
        loginChat.innerHTML = "<h1>Login failed</h1>";
    } else if (alert === '3') {
        authenticate.innerHTML = "<h1>You logged in</h1>";
        document.cookie = "UserToken=" + data['token'];
    } else if (alert === '4') {
        authenticate.innerHTML = "<h1>You are logged in as " + data['username'] + "</h1>";
    }

}
