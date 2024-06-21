$( function() {
    const _locations = JSON.parse({{ locationnames | tojson }});

    var availableLocations = [];
    for (const _location of _locations){
      availableLocations.push(_location.name + ', ' + _location.postal);
    }
    $( "#searchtext" ).autocomplete({
      source: availableLocations
    });
  } );

  $('#searchtext').keypress(function(event) {
    if (event.keyCode == 13) {
      find();
    }
  });

  $('#searchbutton').click(function(event) {
    find();
  });

  function find(){
    var _val = document.getElementById('searchtext').value;
    window.location.replace('/search/' + _val);
  }
