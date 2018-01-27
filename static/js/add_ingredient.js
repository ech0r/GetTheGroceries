var room = 1;
var test = document.getElementById('test')
test.innerHTML = 'Javascript Works!'
function ingredient_fields() {

    room++;
    var objTo = document.getElementById('ingredient_fields');
    var divtest = document.createElement("div");
	divtest.setAttribute("class", "form-group removeclass"+room);
	var rdiv = 'removeclass'+room;
    divtest.innerHTML = '<div><p>Button Works!</p></div><object type="text/html" data="/templates/ingredient_row.html"></object>';
    objTo.appendChild(divtest)
}
   function remove_ingredient_fields(rid) {
	   $('.removeclass'+rid).remove();
   }
