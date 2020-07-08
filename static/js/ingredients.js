function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

function ingredient_fields(ingredient=false, amount=false, unit=false) {
    var uuid = uuidv4();
    var ingr_value = ingredient ? `value="${ingredient}"`:`placeholder="Name"`;
    var amount_value = amount ? `value="${amount}"`:`placeholder=Amount`;
    var unit_index = unit;
    var ingrs = document.getElementsByClassName("ingredient-field");
    var button =  `
        <button class="ingredient-button btn btn-danger" type="button" onclick="remove_ingredient_fields(this.parentElement.parentElement.id)" id="minus-button"> 
            <i class="fa fa-minus-square" aria-hidden="true"></i> 
        </button>`;
    if (ingrs.length > 0) {
        button =  `
        <button class="ingredient-button btn btn-danger" type="button" onclick="remove_ingredient_fields(this.parentElement.parentElement.id)" id="minus-button"> 
            <i class="fa fa-minus-square" aria-hidden="true"></i> 
        </button>`;
        var ingredient_buttons = document.getElementsByClassName("ingredient-button");
        for (var i=0; i < ingredient_buttons.length|0; i = i + 1|0) {
            ingredient_buttons[i].setAttribute("class","ingredient-button btn btn-danger");
            ingredient_buttons[i].setAttribute("onclick", "remove_ingredient_fields(this.parentElement.parentElement.id)");
            ingredient_buttons[i].setAttribute("id", "minus-button")
            ingredient_buttons[i].innerHTML = '<i class="fa fa-minus-square" aria-hidden="true"></i>'
        }
    } 
    var ingrBody = document.getElementById('ingredient_body');
    var ingrField = document.createElement("div");
    ingrField.setAttribute("id", uuid);
    ingrField.setAttribute("class", "ingredient-field input-group");
    var ingrFieldHtml = button ? `
    <input type="text" class="form-control" name="ingr_name" id="name" ${ingr_value} required> 
    <input type="number" step="0.01" min="0" max="999" class="form-control" name="amount" id="amount" ${amount_value} required> 
    <select id="${uuid}_select" required name="unit" class="form-control"></select> 
    <div class="input-group-append"> ${button}</div>`:`<input type="text" class="form-control" name="ingr_name" id="name" ${ingr_value} required> 
    <input type="number" step="0.01" min="0" max="999" class="form-control" name="amount" id="amount" ${amount_value} required> 
    <select id="${uuid}_select" required name="unit" class="form-control"></select>`;
    ingrField.innerHTML = ingrFieldHtml;
    ingrBody.appendChild(ingrField)
    var select = document.getElementById(uuid + "_select");
    var unittype = ['kg', 'g', 'lb', 'oz', 'L', 'mL', 'Tblsp', 'tsp', 'cup', 'quart', 'gallon', 'package', 'jar', 'qty']
    unittype.forEach(function(element, key) {
        if (element === unittype[unit_index]) {
            select[key] = new Option(element,key, true, true);
        } else {
            select[key] = new Option(element,key);
        }
    });
}

function edit_ingredient_fields(ingredients, amounts, units)
{
    for (var i=0; i < ingredients.length; i++)
    {
        ingredient_fields(ingredients[i], amounts[i], units[i]);
    }
}

function remove_ingredient_fields(rid) {
    var element = document.getElementById(rid);
    if (document.getElementsByClassName("ingredient-field").length > 1) {
        element.remove();
    } else {
        var buffer = document.getElementById("message-buffer");
        buffer.innerHTML = `<div class="alert alert-danger">Recipes must have at least one ingredient.</div>`;
        setTimeout(function(){
            $('.alert').delay(2000).fadeOut();
        }, 2000);
    }
}