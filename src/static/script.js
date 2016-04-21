function create_action(url, ask_confirm=false) {
	return function() {
		if (ask_confirm) {
			if (!confirm("Are you really sure?")) {
				return;
			}
		}
		
		$.post(url, function(rawdata) {
			if (rawdata != "") {
				console.log(rawdata);
				data = $.parseJSON(rawdata);
				if (data.message != null) {
					alert(data.message);
				}
			}
		});
	}
}

$(document).ready(function() {
	console.log("Ready...");
	
	$("#ardu-start").click(create_action("/ajax/arducopter/start"));
	$("#ardu-start-without-connection").click(create_action("/ajax/arducopter/start_without_connection"));
	$("#ardu-stop").click(create_action("/ajax/arducopter/stop", true));

	$("#power-shutdown").click(create_action("/ajax/power/shutdown", true));
	$("#power-reboot").click(create_action("/ajax/power/reboot", true));
});
