// Work to be done: Server Accessable, Make Assets, Combine w/ User info stored in server, Put usernames on diff canvas layer
// Work to be done: fix names, player movement
// Possible ideas - add Emotes

// List of variables grabbed from html document
// Buttons
var start_button = document.getElementById("start");
var reset_button = document.getElementById("reset");
// Input Values
var name_input = document.getElementById("username");
var male_input = document.getElementById("male");
var female_input = document.getElementById("female");
// Canvas
var background = document.getElementById("board");
var add_background = background.getContext("2d");
background.width  = background.offsetWidth;
background.height = background.offsetHeight;
var players = document.getElementById("player");
var add_player = players.getContext("2d");
players.width  = players.offsetWidth;
players.height = players.offsetHeight;


// Start states of certain elements in html
reset_button.disabled = true;
male_input.checked = true;


// Current user information
var username = "";
var model = "";
var current_x = 0
var current_y = 0


// Draw background function
function draw_background(){
    // Draws images onto base canvas
    add_background.fillStyle = "white";
    add_background.fillRect(0, 0, background.width, background.height);
}


// create User model function
function draw_user(g){
    // Generate random spawn on map & updates on user info
    var x = Math.floor(Math.random() * (background.width - 50));
    var y = Math.floor(Math.random() * (background.height - 50));
    current_x = x;
    current_y = y;

    // Draws model
    if (g == "male"){
        add_player.fillStyle = "#40c2ff";
    } else {
        add_player.fillStyle = "#ff4640";
    }
    add_player.fillRect(x, y, 50, 50);

    // Draws name
    add_player.fillStyle = "black";
    add_player.font = "30px Arial";
    add_player.fillText(username, x, y);
}


// Function for when START button is clicked
start_button.addEventListener("click", function(){
    // Disable start button, enable reset button
    start_button.disabled = true;
    reset_button.disabled = false;

    // Get username and replace harmful variables with good ones
    username = username.replace("&", "&amp");
    username = username.replace("<", "&lt");
    username = username.replace(">", "&gt");

    // Get model information
    if (male_input.checked){
        model = "male";
    } else {
        model = "female";
    }

    // Draw the base background
    draw_background();

    // Draw player onto board
    draw_user(model);
});

// Function for when RESET button is clicked
reset_button.addEventListener("click", function(){
    // Disable reset button, enable start button
    start_button.disabled = false;
    reset_button.disabled = true;

    // Clears out user model from board
    add_player.clearRect(current_x, current_y, 50, 50);
})