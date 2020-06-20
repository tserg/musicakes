function validateForm() {
	var x = document.forms["new_user"]["username"].value;

	if (x.length < 6 || x.length > 20) {
		alert("Username must be between 6 to 20 characters.");
		return false;
	}

	if (/^[a-zA-Z0-9- ]*$/.test(x) == false) {
		alert("Username cannot contain special characters.");
		return false;
	}
}