import { IP_ADDRESS } from './Settings.js'
var socket;

// Function Executes when the webpage is loaded
window.onload = async function fetchText() {
    let response = await fetch(IP_ADDRESS + "/devices");
    let data = await response.json();
    socket = io.connect(IP_ADDRESS); //, {transports: [websocket]});

    // Loop through the devices and create a container for them with elements
    for(var i = 0; i < data.data.length; i++) {
        // Create a div 'container'
        const device = document.createElement('div');
        device.id = "container";

        // Create Header for device name
        const header = document.createElement('h1');

        // Set innerHTML to device name inside the header element
        header.innerHTML = data.data[i].device_name;
        header.className = "device_name";

        // Append header to 'div' container
        device.appendChild(header);

        // Create Button Element -----
        const btn = document.createElement('input');
        btn.type = "checkbox";
        btn.id = "switch" + i
        btn.checked = data.data[i].status;
        btn.className = data.data[i].identifier;
        const label = document.createElement('label')
        label.setAttribute("for", "switch" + i);

        // Add Event Listener to that button with the class name = device name
        btn.addEventListener("click", function (event) 
        {
            handleClick(event, btn.className);
            btn.disabled = true
            setTimeout(()=> {
                btn.disabled = false
            }, 4500)
        }, false);

        const name_change_btn = document.createElement('button');
        name_change_btn.innerHTML = 'Change Device Name'
        name_change_btn.type = "submit"
        name_change_btn.onclick = function() {
            location.href = IP_ADDRESS + "/devices/" + btn.className;
        }

        device.appendChild(btn);
        device.appendChild(label);
        device.appendChild(name_change_btn);

        // Grab the element we want to insert the new container into
        const current_div = document.getElementById("display_dock");
        current_div.appendChild(device);
    }
    CreateSettingsButton()
}

// Creates the Settings and Refresh Button
function CreateSettingsButton() {
    // Create Settings Block Div
    const settings_block = document.createElement('div');
    settings_block.className = "settings_block";

    // Create Button element
    const btn_1 = document.createElement('button');
    btn_1.className = "refresh_btn";
    btn_1.innerHTML = "Refresh";
    btn_1.onclick = function() {
        window.location.reload();
    }

    settings_block.append(btn_1);
    const curr = document.getElementById('settings_block');
    curr.append(settings_block);

}

// Function determines which button pressed
function handleClick(event, device_name) {
    event = event || window.event;

    var element = event.target;

    // Climb up the document tree from the target of the event
    while (element) {
        if (element.nodeName === "INPUT" && device_name == element.className) {
            // The user clicked on a <button> or clicked on an element inside a <button>
            Change_Pin_Status(element.className);
            break;
        }

        element = element.parentNode;
    }
};

// Sends a request by socket to communicate with arduino and toggle a pin HIGH/LOW
function Change_Pin_Status(device_name) {
        socket.emit('status_update_db', device_name);
};

// Sends a request by socket to update the clock on MAX7219 Dot Matrix
var UpdateClock = window.setInterval(function() {
    socket.emit('update_clock', 'update_request')
}, 5000);

