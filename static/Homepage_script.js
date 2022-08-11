window.onload = async function fetchText() {
    let response = await fetch('http://localhost:5001/devices');
    let data = await response.json();
    console.log(data);

    for(var i = 0; i < data.data.length; i++) {
        // Create a div 'container'
        const device = document.createElement('div');
        const identifier = document.createTextNode(data.data[i].identifier);
        device.appendChild(identifier);

        // Grab the element we want to insert the new container into
        const current_div = document.getElementById("display_dock");
        current_div.appendChild(device);
    }
}