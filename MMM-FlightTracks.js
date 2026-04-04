/*
 * Magic Mirror flight tracking module 
 * @author jdanek
 */

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

Module.register("MMM-FlightTracks", {

	// create flight data dictionary
	flight_info : {
		"timestamp" : "No Flights",
		"callsign" : "n/a",
		"airline" : "n/a",
		"aircraft" : "n/a",
		"altitude" : "n/a",		 
		"velocity" : "n/a",		 
		"track" : "n/a",		
		"route" : ["n/a", "n/a", "n/a", "n/a"], // [start_airport, start_location, end_airport, end_location]
		"active" : false,
		"curr_count" : 0,
		"max_count" : 0
	},

	// default config values if not supplied in config.js
	defaults: {
		debug: false,				// enable python debug log level
		country_code: "US",			// (ISO-2) used for postal code lookup and also to omit country name in airport location
		units: "IMPERIAL", 			// (IMPERIAL | METRIC) used to display aircraft speed and altitude
		max_width: "28",			// truncate aircraft and airport text fields to fit allowable space
		no_flight_timer: 60,		// (secs) polling wait time when no flights are returned
		single_flight_timer: 30,	// (secs) time to display a single flight
		multiple_flight_timer: 15,	// (secs) time to display each flight
		postal_width: 10,			// (km) postal code width (longitudinal) 
		postal_height: 10,			// (km) postal code height (latitudinal) 
	},

	init: function () {
		Log.log("MMM-FlightTracks is in init");
	},
  
	start: function () {
		Log.log(this.name + " is starting");
	},

	loaded: function (callback) {
		Log.log(this.name + " is loaded");
		callback();
	},


	// only called if the module header was configured in module config in config.js
	getHeader: function () {
		return this.data.header;
	},

	// messages received from other modules and the system  
	notificationReceived: function (notification, payload, sender) {
		if (sender) {
			Log.log(this.name + " received a module notification: " + notification + " from sender: " + sender.name);
		} else {
			Log.log(this.name + " received a system notification: " + notification);
		}

		if (notification === "ALL_MODULES_STARTED") {
		  this.sendSocketNotification("DO_FLIGHT_TRACKS_API", this.config)
		}
	},


	// messages received from from node helper  
	socketNotificationReceived: function (notification, payload) {
		Log.log(this.name + " received a socket notification: " + notification);
		if (notification === "FLIGHT_DATA") {
			try {
				const flights = JSON.parse(payload.output);
				Log.log(this.name + " flights.length: " + flights.length);

				if( flights.length > 1) {
					const runLoopWithDelay = async () => {
						curr_count = 0;
						for (const flight of flights) {
							this.flight_info = flight;
							this.flight_info.active = true;
							this.flight_info.max_count = flights.length;
							curr_count += 1;
							this.flight_info.curr_count = curr_count;
							this.updateDom();
							await sleep(this.config.multiple_flight_timer * 1000); 	
						}
						this.sendSocketNotification("DO_FLIGHT_TRACKS_API", this.config);
					}
					runLoopWithDelay();
				}
				else if (flights.length == 1)
				{
					this.flight_info = flights[0];
					this.flight_info.active = true;
					this.flight_info.max_count = 1;
					this.flight_info.curr_count = 1;
					this.updateDom();
					setTimeout(() => {
						this.sendSocketNotification("DO_FLIGHT_TRACKS_API", this.config)
					}, this.config.single_flight_timer * 1000);  
				}
				else {
					this.flight_info.active = false;
					this.flight_info.max_count = 0;
					this.flight_info.curr_count = 0;
					this.updateDom();
					setTimeout(() => {
						this.sendSocketNotification("DO_FLIGHT_TRACKS_API", this.config)
					}, this.config.no_flight_timer * 1000);  
				}
			} 
			catch (err) {
				Log.error(this.name + " Flight data error:", err);  
				setTimeout(() => {
					this.sendSocketNotification("DO_FLIGHT_TRACKS_API", this.config)
				}, 300 * 1000);  
			}
		}
	},

	// system notification your module is being hidden
	// typically you would stop doing UI updates (getDom/updateDom) if the module is hidden
	suspend: function () {

	},

	// system notification your module is being unhidden/shown
	// typically you would resume doing UI updates (getDom/updateDom) if the module is shown
	resume: function () {

	},

	/* 
	getDom: function () {
		var wrapper = document.createElement("div");
		wrapper.innerHTML = this.flight_info;
		return wrapper;
	},
	*/

	getStyles () {
    return ["MMM-FlightTracks.css"];
  	},

	getTemplate: function () {
		return "MMM-FlightTracks.njk";
	},

	getTemplateData: function () {
		this.flight_info["config"] = this.config
		return (this.flight_info);
	}
})