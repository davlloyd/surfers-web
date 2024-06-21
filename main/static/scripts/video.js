function setVideo(num){
  var i;
  for (i = 1; i <= num; i++) { 
    videojs('video-' + i).ready(function(){
      var myPlayer = this, id = myPlayer.id();
      var aspectRatio = 264/640; 
      function resizeVideoJS(){
        var width = document.getElementById(id).parentElement.offsetWidth;
        myPlayer.width(width);
        //myPlayer.height( width * aspectRatio );
      }
      resizeVideoJS();
      window.onresize = resizeVideoJS; 
    });
  }
}
