function validateForm() {
	var x = document.forms["new_user"]["username"].value;

	if (x.length < 1 || x.length > 100) {
		alert("Username must be between 1 to 100 characters.");
		return false;
	}

	if (/^[a-zA-Z0-9- ]*$/.test(x) == false) {
		alert("Username cannot contain special characters.");
		return false;
	}

	if (x.indexOf(' ') >= 0) {
		alert("Username cannot contain a space.");
		return false;
	}

}