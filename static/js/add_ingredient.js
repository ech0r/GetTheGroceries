var num = 1;
function ingredient_fields() {
    var objTo = document.getElementById('ingredient_body');
    var divtest = document.createElement("div");
	divtest.setAttribute("class", "form-group removeclass"+num);
	var rdiv = 'removeclass'+num;
    divtest.innerHTML = '<div id="ingredient_field"> <div class="col-xs-4 nopadding"> <div class="form-group"> <input type="text" class="form-control" name="ingr_name" id="name" placeholder="Ingredient Name" required> </div> </div> <div class="col-xs-3 nopadding"> <div class="form-group"> <input type="number" step="0.01" min="0" max="999" class="form-control" name="amount" id="amount" placeholder="Amount" required> </div> </div> <div class="col-xs-3 nopadding"> <div class="form-group"> <div class="input-group"> <select name="unit" class="form-control"> <option value="kg">kg</option> <option value="g">g</option> <option value="lb">lb</option> <option value="oz">oz</option> <option value="L">L</option> <option value="mL">mL</option> <option value="Tblsp">Tblsp</option> <option value="tsp">tsp</option> <option value="cup">cup</option> <option value="box">box</option> <option value="jar">jar</option> <option value="pkg">pkg</option> <option value="box">box</option> </select> <div class="input-group-btn"> <button class="btn btn-danger" type="button" onclick="remove_ingredient_fields('+ num +');" id="minus-button"><span class="glyphicon glyphicon-minus" aria-hidden="true"></span></button> </div> </div> </div> </div></div>'
    objTo.appendChild(divtest)
    num++;
}
   function remove_ingredient_fields(rid) {
	   $('.removeclass'+rid).remove();
   }
