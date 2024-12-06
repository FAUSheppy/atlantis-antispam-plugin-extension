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
        return await response.json();
    })
}

function iterate_message(msg_part_obj){

    parts = []
    /* iterate over parts if parts exist */
    if(msg_part.parts){
        for part in msg_part.parts:
            parts += iterate_message(part)
    
    return [msg_part] + parts

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
    if(message_obj.message_obj.length != 1){
        return
    }

    /* get message id */
    let msg_id = message_obj.messages[0].id

    /* get full message with body/parts from id */
    browser.messages.getFull(msg_id).then(obj => {

        /* iterate over message to get all parts */
        let msg_part_array = iterate_message(obj)

        /* send out the array to the server */
        let result = send_parts(part_array)

        /* output result */
        console.log(result)

        /* TODO display a result indicator icon */

        /* TODO set an alt-message on hover */

    })
  });
});
