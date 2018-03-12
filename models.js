var weyl_File = "builder/weyl.sage";
var class_file = "builder/classes/model.sage";
var refl_File = "builder/reflections.sage";
var cellInfo = "";
function classInsert(callback) {
  $.get(class_file, function(data) {
    $('#sage_script').prepend(data);
    callback();
  });
}
function makeCells() {
    if (cellInfo != "") {
      sagecell.deleteSagecell(cellInfo);
      $(".cell_container").append($("<div id='main' class='sage'></div>"));
    }
    cellInfo = sagecell.makeSagecell({"inputLocation": ".sage",
                           editor: "codemirror-readonly",
                           //evalButtonText: 'Create Model',
                           codeLocation: '#sage_script',
                           autoeval: true,
                           hide: ['editor', 'evalButton']
                           });
    var button_element = document.getElementById('get_models').innerHTML;
    if (button_element == "") {
      $("#get_models").append($("<button type ='submit' onclick='get_file()'>Generate STL</button><br/>"));
    }
}
function model(file, cellMaker) {
  $.get(file, function(data){
    $("#sage_script").empty().append(data);
    classInsert(function() {
      if (typeof cellMaker === "function") {
        cellMaker();
      }
    });
  });
}
function get_file() {
  // send file as needed
  $('#get_models').prepend($("<div id='message'><p>Make sure you\'ve clicked 'Create model' and chosen what parameters to use. This may take several minutes. A download window will appear when the STL file has been generated.</p></div>"));
  $('#message').append("<img src=assets/ajax-loader.gif><br/>");
  var data = document.getElementById('scad').innerHTML;
  console.log(data);

  var stl_post = $.ajax({
    type: "POST",
    url: "/generate_stl",
    data: data,
    success: function(response) {
      console.log(response);
      download("output.stl", response);
    },
    contentType: "text/plain"})
    .always(function () {
      $('#message').remove();
    })
    .fail(function() {
      alert("Could not generate stl file");
    })
}

function download(filename, text) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    element.setAttribute('download', filename);

    element.style.display = 'none';
    document.body.appendChild(element);

    element.click();

    document.body.removeChild(element);
}
