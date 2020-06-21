function validateForm() {
	var x = document.forms["new_artist"]["artist_name"].value;

	if (x.length < 1 || x.length > 100) {
		alert("Artist name must be between 1 to 100 characters.");
		return false;
	}

	if (/^[a-zA-Z0-9- ]*$/.test(x) == false) {
		alert("Artist name cannot contain special characters.");
		return false;
	}

	if (x[0] == ' ') {
		alert("Artist name cannot start with a space.");
		return false;
	}

}