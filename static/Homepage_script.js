window.onload = async function fetchText() {
    let response = await fetch('http://192.168.1.250:5001/devices');
    let data = await response.json();
    console.log(data);

    for(var i = 0; i < data.data.length; i++) {
        // Create a div 'container'
        const device = document.createElement('div');
        device.id = "container";

        // Create Header for device name
        const header = document.createElement('h1');

        // Set innerHTML to device name inside the header element
        header.innerHTML = data.data[i].identifier;

        // Append header to 'div' container
        device.appendChild(header);

        // Create Button Element
        const btn = document.createElement('input');
        btn.type = "checkbox";
        btn.id = "switch" + i
        btn.className = data.data[i].identifier;
        const label = document.createElement('label')
        label.setAttribute("for", "switch" + i);
        label.innerHTML = "Toggle";

        // Add Event Listener to that button with the class name = device name
        btn.addEventListener("click", function (event) {
            handleClick(event, btn.className);
        }, false);

        device.appendChild(btn);
        device.appendChild(label);

        // Grab the element we want to insert the new container into
        const current_div = document.getElementById("display_dock");
        current_div.appendChild(device);
    }
}

function handleClick(event, device_name) {
    event = event || window.event;
    event.target = event.target || event.srcElement;

    var element = event.target;

    // Climb up the document tree from the target of the event
    while (element) {
        if (element.nodeName === "INPUT" && device_name == element.className) {
            // The user clicked on a <button> or clicked on an element inside a <button>
            Change_Pin_Status(element, element.className);
            break;
        }

        element = element.parentNode;
    }
};

async function Change_Pin_Status(button, device_name) {
    console.log("Button Pressed");
    // Grab Current Device_Status
    let response = await fetch('http://192.168.1.250:5001/devices/' + device_name);
    // Parse into Json Format
    let data = await response.json();
    // If status == 0  then set to 1, else set to 0
    if(data.status == 0){
        fetch('http://192.168.1.250:5001/devices/' + device_name + "/1");
    } else {
        fetch('http://192.168.1.250:5001/devices/' + device_name + "/0");
    }
}