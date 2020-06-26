tracks_count = $('.track-form-group').length;

/* sanity check */

const createReleaseButton = document.querySelector('#create-release-btn');

createReleaseButton.addEventListener('click', () => {
  validateForm().then(function(response) {
    if (response) {
      var release_name = document.getElementById('release-name-input').value;
      var release_price = document.getElementById('release-price-input').value;
      var release_cover_art = document.getElementById('release-cover-art-input').files[0];
      var release_text = document.getElementById('release-text-input').value;

      addRelease(release_name, release_price, release_cover_art, release_text);

    }

    else {

      return false;

    }
  })
});

async function validateForm() {
  
  // validate release

  var release_name = document.getElementById('release-name-input');
  var release_cover_art = document.getElementById('release-cover-art-input').files[0];

  if (!release_cover_art) {
    alert("You have not uploaded a cover art.");
    return false;
  }

  release_cover_art_extension = release_cover_art.name.split('.').pop();

  if (release_name[0] == ' ') {
      alert("Release name cannot start with a space.");
      return false;
  }

  // validate tracks

  const track_name_placeholder = "track-name-input"
  const track_file_placeholder = "track-file-input"
  const track_price_placeholder = "track-price-input"  

  for (i=1; i<=tracks_count; i++) {

    var track_name_id = track_name_placeholder + "-" + i.toString();
    var track_name = document.getElementById(track_name_id).value;

    if (track_name[0] == ' ') {
      alert("Track name cannot start with a space.");
      return false;
    }

    var track_file_id = track_file_placeholder + "-" + i.toString();

    var track_file_element = document.getElementById(track_file_id);
    var track_file = track_file_element.files[0];
    var track_file_type = track_file.type;
    var track_file_name = track_file.name;

    if (!track_file) {
      alert("You have not uploaded all the track files.");
      return false;
    }

    if (track_file_name.split('.').pop() != 'wav') {
      alert("You have uploaded files which are not in .WAV format.");
      return false;
    }

  }

  return true;

}

function addRelease(release_name, release_price, release_cover_art, release_text) {

  getSignedRequestCoverArt(release_cover_art, release_name, release_price, release_text);
}

function getSignedRequestCoverArt(file, release_name, release_price, release_text){
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/sign_s3?file_name="+file.name+"&file_type="+file.type);
  xhr.onreadystatechange = function(){
    if(xhr.readyState === 4){
      if(xhr.status === 200){
        var response = JSON.parse(xhr.responseText);

        uploadFileCoverArt(file, response.data, response.url, file.name, release_name, release_price, release_text);
      }
      else{
        alert("Could not get signed URL.");
      }
    }
  };
  xhr.send();
}

function uploadFileCoverArt(file, s3Data, url, file_name, release_name, release_price, release_text){
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
        alert("Cover art uploaded")
        addReleaseToServer(file_name, release_name, release_price, release_text);
      }
      else{
        console.log(error);
        alert("Could not upload file.");
      }
   }
  };
  xhr.send(postData);
}

function addReleaseToServer(file_name, release_name, release_price, release_text) {

  var csrf_token = document.getElementById('csrf_token').value;

  var data = JSON.stringify({
    file_name: file_name,
    release_name: release_name,
    release_price: release_price,
    release_text: release_text
  });

  var xhr = new XMLHttpRequest();
  xhr.open("POST", '/releases/create_2', false);

  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.setRequestHeader("Accept", "application/json");
  xhr.setRequestHeader('X-CSRFToken', csrf_token)

  xhr.onreadystatechange = function(error, result) {
    if(xhr.readyState === 4){
      if(xhr.status === 200){

        response = JSON.parse(xhr.response);

        const release_id = response['release_id'];
        addTracks(release_id);

      }
      else{
        console.log(error);
        alert("Your release could not be created.");
      }
   }
  };
  xhr.send(data);

}

function addTracks(release_id) {

  const track_name_placeholder = "track-name-input"
  const track_file_placeholder = "track-file-input"
  const track_price_placeholder = "track-price-input"  

  for (i=1; i<=tracks_count; i++) {

    var track_name_id = track_name_placeholder + "-" + i.toString();

    var track_name = document.getElementById(track_name_id).value;

    var track_file_id = track_file_placeholder + "-" + i.toString();

    var track_file_element = document.getElementById(track_file_id);

    var track_file = track_file_element.files[0];
    var track_file_name = track_file.name;

    var track_price_id = track_price_placeholder + "-" + i.toString();
    var track_price = document.getElementById(track_price_id).value;

    getSignedRequestTrack(track_file, track_name, track_price, release_id);

  }
  
}

function getSignedRequestTrack(file, track_name, track_price, release_id){
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/sign_s3?file_name="+file.name+"&file_type="+file.type);
  xhr.onreadystatechange = function(){
    if(xhr.readyState === 4){
      if(xhr.status === 200){
        var response = JSON.parse(xhr.responseText);

        uploadFileTrack(file, response.data, response.url, file.name, track_name, track_price, release_id);
      }
      else{
        alert("Could not get signed URL.");
      }
    }
  };
  xhr.send();
}

function uploadFileTrack(file, s3Data, url, file_name, track_name, track_price, release_id) {
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
        alert("Track uploaded")
        addTrackToServer(file_name, track_name, track_price, release_id);
      }
      else{
        console.log(error);
        alert("Could not upload file.");
      }
   }
  };
  xhr.send(postData);
}

function addTrackToServer(file_name, track_name, track_price, release_id) {

  var csrf_token = document.getElementById('csrf_token').value;

  var data = JSON.stringify({
    file_name: file_name,
    track_name: track_name,
    track_price: track_price,
    release_id: release_id
  });

  var xhr = new XMLHttpRequest();
  xhr.open("POST", '/tracks/create');

  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.setRequestHeader("Accept", "application/json");
  xhr.setRequestHeader('X-CSRFToken', csrf_token)

  xhr.onreadystatechange = function(error, result) {
    if(xhr.readyState === 4){
      if(xhr.status === 200){

        response = JSON.parse(xhr.response);

      }
      else{
        console.log(error);
        alert("Your track could not be created.");
      }
   }
  };
  xhr.send(data);

}