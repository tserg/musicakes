function validateForm() {
	var x = document.forms["new_user"]["username"].value;
	console.log(x);
	if (x.length < 6 || x.length > 20) {
		alert("Username must be between 6 to 20 characters");
		return false;
	}
}