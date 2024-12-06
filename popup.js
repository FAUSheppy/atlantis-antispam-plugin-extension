async function send_parts(part_array){

    const url = "http://localhost:5000/test"
    
    let response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(part_array)
    }).then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json()
    })

    return response

}

function iterate_message(msg_part_obj){

    parts = []
    /* iterate over parts if parts exist */
    if(msg_part_obj.parts){
        for(part in msg_part_obj.parts){
            parts.concat(iterate_message(part))
        }
    }
    
    return [msg_part_obj].concat(parts)

}

browser.tabs.query({
  active: true,
  currentWindow: true,
}).then(tabs => {

  /* get current tag id */
  let tabId = tabs[0].id;

  /* get messages display in current tab */
  browser.messageDisplay.getDisplayedMessages(tabId).then(message_obj => {

    /* skip if no message or multi-message view */
    if(message_obj.messages.length != 1){
        console.log("Invalid Message List length", message_obj.message_obj.length)
        return
    }

    /* get message id */
    let msg_id = message_obj.messages[0].id

    /* get full message with body/parts from id */
    browser.messages.getFull(msg_id).then(obj => {

        /* iterate over message to get all parts */
        let msg_part_array = iterate_message(obj)

        /* send out the array to the server */
        let result = send_parts(msg_part_array)
        result.then( j => {
            /* output result */
            console.log("Output", j)
        })

        /* TODO display a result indicator icon */
        el = document.getElementById("test")
        console.log(el)
        el.style.background = "red"
        el.style.min_height = "50px"
        el.innerHTML = "wtf"

        /* TODO set an alt-message on hover */

    })
  });
});
