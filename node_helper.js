/*
 * Magic Mirror flight tracking helper module 
 * @author jdanek
 */

var NodeHelper = require("node_helper");
const { spawn } = require("child_process");


module.exports = NodeHelper.create({

	init(){
		console.log("init module helper MMM-FlightTracks");
	},

	start() {
		console.log('Starting module helper:' +this.name);
	},

	stop(){
		console.log('Stopping module helper: ' +this.name);
	},

	// handle messages from this module 
	socketNotificationReceived(notification, payload) {
		console.log(this.name + " helper received a socket notification: " + notification + " - Payload: " + payload);
		
		if(notification === "DO_FLIGHT_TRACKS_API") {            
            // spawn the python process with serialized config data
            const config = JSON.stringify(payload);
            console.log(this.name + " helper sending config to python:" + config)
            const pythonProcess = spawn('python3', ['./modules/MMM-FlightTracks/flight_tracks.py', config]);
            
            let scriptOutput = "";
            pythonProcess.stdout.on('data', (data) => {
                // accumulate output from the python script
                scriptOutput += data.toString();
            });

            pythonProcess.on('close', (code) => {
                // when the script finishes, send the data back to the module
                if (code != 0) {
                    console.error(this.name + ` python code: ${code}, output: ${scriptOutput}`);
                }
                else {
                    console.log(this.name + ` python code: ${code}, output: ${scriptOutput}`);
                }
                this.sendSocketNotification('FLIGHT_DATA', {output: scriptOutput});
            });
		}
	}
});
