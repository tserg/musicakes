$('.download-track-btn').on("click", function() {

	const download_track_id = $(this).attr('id');

	getSignedRequestDownloadTrack(download_track_id);

});

$('.download-release-btn').on("click", function() {

	const download_release_id = $(this).attr('id');

	downloadRelease(download_release_id);

});


function getSignedRequestDownloadTrack(track_id) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", "/sign_s3_download?track_id="+track_id);
  xhr.onreadystatechange = function(){
    if(xhr.readyState === 4){
      if(xhr.status === 200){
        var response = JSON.parse(xhr.responseText);

        downloadTrack(response.data, response.file_name);
      }
      else{
        alert("There was a problem with your download. Please refresh and try again.");
      }
    }
  };
  xhr.send();
}

function downloadTrack(presigned_url, file_name) {
	var xhr = new XMLHttpRequest();
	xhr.open("GET", presigned_url);
	xhr.responseType = 'blob';
	xhr.onreadystatechange = function(){
	    if(xhr.readyState === 4){
	      if(xhr.status === 200){
	        var blob = xhr.response;
	        saveBlob(blob, file_name);
	      }
	      else{
	      	console.log(xhr.response);
	        alert("There was a problem with your download. Please refresh and try again.");
	      }
	    }
	 };
	 xhr.send();
}

function saveBlob(blob, file_name) {
	var a = document.createElement('a');
	a.href = window.URL.createObjectURL(blob);
	a.download = file_name;
	a.dispatchEvent(new MouseEvent('click'));
}

function downloadRelease(release_id) {

	var xhr = new XMLHttpRequest();
	xhr.open("GET", "/releases/" + release_id + "/download");

  	xhr.onreadystatechange = function(){
    	if(xhr.readyState === 4){
	      	if(xhr.status === 200){

	      		tracks = JSON.parse(xhr.response).track_ids;

	        	tracks.forEach(function(item) {
	        		getSignedRequestDownloadTrack(item);
	        	})
	        }
	  	}

	};
	xhr.send();
}
