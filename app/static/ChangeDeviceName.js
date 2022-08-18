var socket;
window.onload = async function() {
    socket = io.connect('http://192.168.1.250:5001/');

    const btn = document.getElementById('change_name');
    btn.addEventListener("click", function(event) {
        console.log("Button Clicked!");
        ButtonPressed();
        btn.disabled = true;
        setTimeout(() => {
            btn.disabled = false;
        }, 100)
    })
}

function ButtonPressed(){
    const current_device_name = document.getElementById('device_name_change').value;
    const new_device_name = document.getElementById('device_name').value;
    Update_Device_Name(current_device_name, new_device_name);
}

function Update_Device_Name(current_device_name, new_device_name) {
    let msg = [current_device_name, new_device_name];
    socket.emit('update_device_name', msg);
    console.log("Message Sent: " + msg);

    socket.on('Failed', function(data) {
        console.log(data);
    });
    socket.on('Device_Name_Updated', function(data) {
        console.log(data);
    });
}

//window.onload = async function (){
//
//    let change_device_name_form = document.getElementById('device_change_form');
//
//    change_device_name_form.addEventListener("submit", async (e) => {
//        e.preventDefault();
//
//        let form = e.currentTarget;
//        let url = form.action;
//
//        try {
//            let formData = new FormData(form)
//            for (var [key, value] of formData.entries()) { 
//                console.log(key, value);
//            }            let responseData = await postFormFieldsAsJson( {url, formData} );
//            let { serverDataResponse } = responseData;
//            console.log(serverDataResponse);
//
//        } catch (error) {
//            console.error(error)
//        }
//    });
//};
//
//async function postFormFieldsAsJson( { url, formData } ) {
//
//    //Create an object from the form data entries
//    let formDataObject = Object.fromEntries(formData.entries());
//    // Format the plain form data as JSON
//    let formDataJsonString = JSON.stringify(formDataObject);
//
//    //Set the fetch options (headers, body)
//    let fetchOptions = {
//        //HTTP method set to POST.
//        method: "POST",
//        //Set the headers that specify you're sending a JSON body request and accepting JSON response
//        headers: {
//            "Content-Type": "application/json",
//            Accept: "application/json",
//        },
//        // POST request body as JSON string.
//        body: formDataJsonString,
//    };
//
//    //Get the response body as JSON.
//    //If the response was not OK, throw an error.
//    let res = await fetch(url, fetchOptions);
//
//    //If the response is not ok throw an error (for debugging)
//    if (!res.ok) {
//        let error = await res.text();
//        throw new Error(error);
//    }
//    //If the response was OK, return the response body.
//    return res.json();
//}
