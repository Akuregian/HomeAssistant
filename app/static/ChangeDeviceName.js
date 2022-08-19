var socket;
window.onload = async function() {
    socket = io.connect('http://192.168.1.250:5001/');

}