var weyl_File = "weyl-short.sage";
var test = "classes/model.sage";
var short_refl_File = "dev_models-short.sage";
var refl_File = "refl-models.sage";
var dummy = "dummy.sage";
var cellInfo = "";
function classInsert(callback) {
  $.get(test, function(data) {
    $('#sage_script').prepend(data);
    // console.log("Got classInsert called");
    callback();
  });
}
function makeCells() {
    if (cellInfo != "") {
      //console.log(cellInfo);
      sagecell.deleteSagecell(cellInfo);
      $(".cell_container").append($("<div id='main' class='sage'></div>"));
    }
    cellInfo = sagecell.makeSagecell({"inputLocation": ".sage",
                           editor: "codemirror-readonly",
                           evalButtonText: 'Create Model',
                           codeLocation: '#sage_script',
                           hide: ['editor']
                           });
}
function model(file, cellMaker) {
  $.get(file, function(data){
    $("#sage_script").empty().append(data);
    // classInsert();
    classInsert(function() {
      if (typeof cellMaker === "function") {
        cellMaker();
      }
    });
  });
}
function get_file() {
  // send file as needed
  var data = document.getElementById('scad').innerHTML;
  // console.log(data);
  return data;
}
