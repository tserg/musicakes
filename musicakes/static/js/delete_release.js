const deleteReleaseButton = document.querySelector('#delete-release-btn');
const release_id = parseInt(window.appConfig.release_id.address);

console.log(deleteReleaseButton);
console.log(release_id);

deleteReleaseButton.addEventListener('click', () => {

  deleteRelease(release_id);

});

function deleteRelease(release_id) {

  var csrf_token = document.getElementById('csrf_token').value;

  var xhr = new XMLHttpRequest();
  xhr.open("POST", '/releases/' + release_id.toString() + "/delete");

  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.setRequestHeader("Accept", "application/json");
  xhr.setRequestHeader('X-CSRFToken', csrf_token)

  xhr.onreadystatechange = function(error, result) {
    if(xhr.readyState === 4){
      if(xhr.status === 200){

        console.log("Release has been deleted.");
        alert("Your release has been deleted.");
        window.location.replace('/home');

      }
      else{
        console.log(error);
        alert("Your release could not be deleted.");
      }
   }
  };
  xhr.send();

}
