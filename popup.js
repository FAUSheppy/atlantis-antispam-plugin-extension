async function send_parts(part_array){

    const url = "http://localhost:5000/test"
   
    let response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(part_array)
    })

    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    return await response.json()
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

async function move_message_to_junk(msg_id){
    
    const accounts = await browser.accounts.list();
    const message = await browser.messages.get(msg_id);
    // Find the account associated with the message
    const account = accounts.find(acc => message.folder.accountId === acc.id);

    junkFolder = account.junkFolder
    if (!junkFolder) {
      // If no junkFolder is defined, search for a folder named "Junk" or other fallback
      const folders = await browser.folders.getSubFolders(account.id);
      const fallbackFolder = folders.find(folder => folder.name.toLowerCase() === "trash");
      if (fallbackFolder) {
        junkFolder = fallbackFolder.id;
      }
    }

    if (!junkFolder) {
      console.error("No junk folder found for the account (and no fallback).");
      return;
    } 

    try{
      // Move the message to the junk folder of the same account
      await browser.messages.move([msg_id], junkFolder);
      console.log(`Message ${msg_id} moved to the junk folder of the same account.`);
    } catch (error) {
      console.error("Failed to move the message to the junk folder:", error);
    }
}

browser.tabs.query({
  active: true,
  currentWindow: true,
}).then(main)

async function main(tabs){

  /* get current tag id */
  let tabId = tabs[0].id;

  /* get messages display in current tab */
  message_obj = await browser.messageDisplay.getDisplayedMessages(tabId)

  /* skip if no message or multi-message view */
  if(message_obj.messages.length != 1){
      console.log("Invalid Message List length", message_obj.message_obj.length)
      return
  }


  /* get message id */
  let msg_id = message_obj.messages[0].id

  /* get full message with body/parts from id */
  obj = await browser.messages.getFull(msg_id)

  /* iterate over message to get all parts */
  let msg_part_array = iterate_message(obj)

  /* send out the array to the server */
  let result = send_parts(obj)
  let test = await result

  /* TODO display a result indicator icon */
  el = document.getElementById("test")
  if("score" in test){
    score = test.score
  }else{
    score = "NaN"
  }
  if("is_spam" in test && test.is_spam){
    el.style.background = "red"
    el.style.min_height = "50px"
    el.innerHTML = `Spam Detected! [score=${score}]`
    move_message_to_junk(msg_id)
  }else{
    el.style.background = "green"
    el.style.min_height = "50px"
    el.innerHTML = `No Spam Detected (which doesn't mean it's 100% safe) [score=${score}!]`
  }

  /* TODO set an alt-message on hover */

}
