import * as messaging from "messaging";

console.log("App Started");
var document = require('document');

import { HeartRateSensor } from "heart-rate";

// Fetch UI elements we will need to change
let hrLabel = document.getElementById("hrm");
let updatedLabel = document.getElementById("updated");

// Keep a timestamp of the last reading received. Start when the app is started.
let lastValueTimestamp = Date.now();

// Initialize the UI with some values
hrLabel.text = "--";
updatedLabel.text = "...";

// This function takes a number of milliseconds and returns a string
// such as "5min ago".
function convertMsAgoToString(millisecondsAgo) {
  if (millisecondsAgo < 120*1000) {
    return Math.round(millisecondsAgo / 1000) + "s ago";
  }
  else if (millisecondsAgo < 60*60*1000) {
    return Math.round(millisecondsAgo / (60*1000)) + "min ago";
  }
  else {
    return Math.round(millisecondsAgo / (60*60*1000)) + "h ago"
  }
}

// This function updates the label on the display that shows when data was last updated.
function updateDisplay() {
  if (lastValueTimestamp !== undefined) {
    updatedLabel.text = convertMsAgoToString(Date.now() - lastValueTimestamp);
  }
}

// Create a new instance of the HeartRateSensor object
var hrm = new HeartRateSensor();

// Declare an event handler that will be called every time a new HR value is received.
hrm.onreading = function() {
  // Peek the current sensor values
  console.log("Current heart rate: " + hrm.heartRate);
  hrLabel.text = hrm.heartRate;
  var millisecondsAgo = Date.now() - lastValueTimestamp
  var data = {'hr' : hrm.heartRate, 'time' : Date.now()}
  if (messaging.peerSocket.readyState === messaging.peerSocket.OPEN && millisecondsAgo >= 2000) {
      //Send object as JSON string to companion
    lastValueTimestamp = Date.now();
    messaging.peerSocket.send(JSON.stringify(data));
  }
}

// Begin monitoring the sensor
hrm.start();

// And update the display every second
setInterval(updateDisplay, 1000);

