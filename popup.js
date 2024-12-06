browser.tabs.query({
  active: true,
  currentWindow: true,
}).then(tabs => {
  let tabId = tabs[0].id;
  console.log(tabId)
  //console.log(browser.messageDisplay.getDisplayedMessages(tabId))
  browser.messageDisplay.getDisplayedMessages(tabId).then(message_obj => {
    console.log("Message_ID", message_obj.messages[0].id)
    browser.messages.getFull( message_obj.messages[0].id).then(obj => {
        console.log("Full", obj.parts[0])
        console.log("Full", obj.parts[0].headers)
        console.log("Full", obj.parts[0].parts[0])
        console.log("Full", obj.parts[0].parts[1])
    })
    //document.body.textContent = message.subject;
  });
});
