var num = 0;
function ingredient_fields() {
    var objTo = document.getElementById('ingredient_body');
    var ingrfield = document.createElement("div");
	ingrfield.setAttribute("class", "inputgroup removeclass"+num);
	ingrfield.setAttribute("id", 'ingredient_field')
    ingrfield.innerHTML = '<div id="ingredient_field" class="input-group"> <input type="text" class="form-control" name="ingr_name" id="name" placeholder="Ingredient Name" required> <input type="number" step="0.01" min="0" max="999" class="form-control" name="amount" id="amount" placeholder="Amount" required> <select required name="unit" class="form-control"><option value="kg" selected>kg</option> <option value="g">g</option> <option value="lb">lb</option> <option value="oz">oz</option> <option value="L">L</option> <option value="mL">mL</option> <option value="Tblsp">Tblsp</option> <option value="tsp">tsp</option> <option value="cup">cup</option> <option value="quart">quart</option> <option value="gallon">gallon</option> <option value="package">package</option> <option value="jar">jar</option> <option value="qty">qty</option></select> <div class="input-group-append"> <button class="btn btn-danger" type="button" onclick="remove_ingredient_fields('+ num +');" id="minus-button"> <i class="fa fa-minus-square" aria-hidden="true"></i> </button> </div></div>'
    objTo.appendChild(ingrfield)
    num++;
}
   function remove_ingredient_fields(rid) {
	   $('.removeclass'+rid).remove();
	   num--;
   }
