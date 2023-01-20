function $(query){
    var res = document.querySelectorAll(query);
    return res.length==1 ? res[0] : res;
}
var DEBUG = true;
var account, passwd = true;
var ispass = false;
$("#submit").onclick = function (){
    account = $("#acc").value;
    passwd = $("#pwd").value;
    if (account && passwd){
        send(`!${account} ${passwd}`);
    } else {
        alert("Can't empty");
    }
}

var ws = new WebSocket("ws://127.0.0.1:9999/");

function send(data) {
    if (ws && ws.readyState == ws.OPEN) {
        ws.send(data);
    }
}

ws.onmessage = function (message){
    var data = message.data;
    if (data.startsWith("!")) {
        alert(data.slice(1));
        ispass = false;
    }
    if (data.startsWith("<")) {
        if (!(ispass)) {
            $("#input").classList.add("hidden");
            $("#main").classList.remove("hidden");
            ispass = true;
        }
        $("#result").textContent = data.slice(1);
    }
}

$("#msg").onkeypress = function(e){
    if (e.keyCode == 13){
        $("#text-submit").click();
    }
}
$("#text-submit").onclick = function (){
    send(`>${$("#msg").value}`);
    $("#msg").value = "";
}
