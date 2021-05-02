const user_id = parseInt(window.appConfig.user_id.id);

const editProfilePictureButton = document.querySelector('#edit-profile-picture-btn');

editProfilePictureButton.addEventListener('click', () => {
  validateForm().then(function(response) {
    if (response) {

      var profile_picture = document.getElementById('image-input').files[0];
      getSignedRequestProfilePicture(profile_picture);

    }

    else {

      return false;

    }
  })
});

async function validateForm() {

  // validate release

  var profile_picture = document.getElementById('image-input').files[0];

  if (!profile_picture) {
    alert("You have not uploaded a picture.");
    return false;
  }

  return true;

}

function getSignedRequestProfilePicture(file){
  var xhr = new XMLHttpRequest();

  var file_name = "profile_picture." + file.type.slice(6);

  xhr.open("GET", "/sign_s3_upload?file_name="+file_name+"&file_type="+file.type);
  xhr.onreadystatechange = function(){
    if(xhr.readyState === 4){
      if(xhr.status === 200){
        var response = JSON.parse(xhr.responseText);

        uploadProfilePicture(file, response.data, response.url, file_name);
      }
      else{
        alert("Could not get signed URL.");
      }
    }
  };
  xhr.send();
}

function uploadProfilePicture(file, s3Data, url, file_name){
  var xhr = new XMLHttpRequest();
  xhr.open("POST", s3Data.url);

  var postData = new FormData();
  for(key in s3Data.fields){
    postData.append(key, s3Data.fields[key]);
  }
  postData.append('file', file);

  xhr.onreadystatechange = function(error, result) {
    if(xhr.readyState === 4){
      if(xhr.status === 200 || xhr.status === 204){
        alert("Profile picture uploaded")
        updatePictureToServer(file_name);
      }
      else{
        console.log(error);
        alert("Could not upload file.");
      }
   }
  };
  xhr.send(postData);
}

function updatePictureToServer(file_name) {

  var csrf_token = document.getElementById('csrf_token').value;

  var data = JSON.stringify({
    file_name: file_name
  });

  var xhr = new XMLHttpRequest();
  xhr.open("PUT", '/users/' + user_id.toString() + '/update_profile_picture', false);

  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.setRequestHeader("Accept", "application/json");
  xhr.setRequestHeader('X-CSRFToken', csrf_token)

  xhr.onreadystatechange = function(error, result) {
    if(xhr.readyState === 4){
      if(xhr.status === 200){

        alert("Your profile picture has been updated.");
        window.location.reload();

      }
      else{
        console.log(error);
        alert("Your profile picture could not be updated.");
      }
   }
  };
  xhr.send(data);

}
