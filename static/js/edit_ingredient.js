var num = 0
function edit_ingredient_fields(ingredients, amounts, units)
{
    for (var i=0; i < ingredients.length; i++)
    {
        var objTo = document.getElementById('ingredient_body');
        var ingrfield = document.createElement("div");
	    ingrfield.setAttribute("class", "input-group removeclass"+num);
	    ingrfield.setAttribute("id", 'ingredient_field')
        ingrfield.innerHTML = '<input type="text" class="form-control" name="ingr_name" id="name" value="' + ingredients[i] + '" required> <input type="number" step="0.01" min="0" max="999" class="form-control" name="amount" id="amount" value="' + amounts[i] + '" required><select required id="select-unit' + i + '" name="unit" class="form-control" value="' + units[i] + '"></select> <div class="input-group-append"> <button class="btn btn-danger" type="button" onclick="remove_ingredient_fields('+ num +');" id="minus-button"> <i class="fa fa-minus-square" aria-hidden="true"></i> </button> </div>'
        var unittype = ['kg', 'g', 'lb', 'oz', 'L', 'mL', 'Tblsp', 'tsp', 'cup', 'quart', 'gallon', 'package', 'jar', 'qty']
        objTo.appendChild(ingrfield);
        var selectunit = document.getElementById('select-unit' + i);
	    for (j = 0; j < unittype.length; j++)
        {
            var option = document.createElement("option");
            option.innerText = unittype[j];
            option.setAttribute("value", unittype[j]);
            if (units[i] === unittype[j])
            {
                option.setAttribute("selected", "selected");
            }
            selectunit.appendChild(option);
        }
        num++;
    }
}

function add_ingredient_fields()
{
    var objTo = document.getElementById('ingredient_body');
    var ingrfield = document.createElement("div");
	ingrfield.setAttribute("class", "input-group removeclass"+num);
	ingrfield.setAttribute("id", 'ingredient_field')
    ingrfield.innerHTML = '<input type="text" class="form-control" name="ingr_name" id="name" placeholder="Ingredient Name" required> <input type="number" step="0.01" min="0" max="999" class="form-control" name="amount" id="amount" placeholder="Amount" required> <select required name="unit" class="form-control"><option value="kg" selected>kg</option> <option value="g">g</option> <option value="lb">lb</option> <option value="oz">oz</option> <option value="L">L</option> <option value="mL">mL</option> <option value="Tblsp">Tblsp</option> <option value="tsp">tsp</option> <option value="cup">cup</option> <option value="quart">quart</option> <option value="gallon">gallon</option> <option value="package">package</option> <option value="jar">jar</option> <option value="qty">qty</option></select> <div class="input-group-append"> <button class="btn btn-danger" type="button" onclick="remove_ingredient_fields('+ num +');" id="minus-button"> <i class="fa fa-minus-square" aria-hidden="true"></i></button></div>'
    objTo.appendChild(ingrfield)
    num++;
}

function remove_ingredient_fields(rid)
{
    $('.removeclass'+rid).remove();
    num--;
}
