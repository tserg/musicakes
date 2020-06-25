tracks_count = $('#track-file-fields .specific-class').length;

console.log(tracks_count);

$('.track-file-fields').change(function() {

  console.log(123);

  var filename = $(this).val()
  console.log(filename);

  var props = $(this).prop('files');
  var file = props[0];
  console.log(file);

  if (file) {
    getSignedRequest(file);
  }

});

function getSignedRequest(file){
  console.log("getSignedRequest triggered");
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/sign_s3?file_name="+file.name+"&file_type="+file.type);
  xhr.onreadystatechange = function(){
    if(xhr.readyState === 4){
      if(xhr.status === 200){
        var response = JSON.parse(xhr.responseText);
        console.log("response");
        console.log(response);
        console.log(response.data);
        console.log(response.url);
        console.log(file);
        uploadFile(file, response.data, response.url);
      }
      else{
        alert("Could not get signed URL.");
      }
    }
  };
  xhr.send();
}

function uploadFile(file, s3Data, url){
  console.log("uploadFile triggered");
  var xhr = new XMLHttpRequest();
  xhr.open("POST", s3Data.url);
  console.log(s3Data.url);
  console.log(url);
  console.log(file);

  var postData = new FormData();
  for(key in s3Data.fields){
    postData.append(key, s3Data.fields[key]);
  }
  postData.append('file', file);

  console.log(postData);

  xhr.onreadystatechange = function(error, result) {
    if(xhr.readyState === 4){
      if(xhr.status === 200 || xhr.status === 204){
        alert("File uploaded")
      }
      else{
        console.log(error);
        alert("Could not upload file.");
      }
   }
  };
  xhr.send(postData);
}
