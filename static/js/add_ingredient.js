function uuidv4() {
    return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
      (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
  }

function ingredient_fields() {
    var objTo = document.getElementById('ingredient_body');
    var ingrfield = document.createElement("div");
    var uuid = uuidv4();
    ingrfield.setAttribute("id", uuid)
    ingrfield.innerHTML = `
    <div id="" class="ingredient-field input-group"> 
        <input type="text" class="form-control" name="ingr_name" id="name" placeholder="Ingredient Name" required> 
        <input type="number" step="0.01" min="0" max="999" class="form-control" name="amount" id="amount" placeholder="Amount" required> 
        <select required name="unit" class="form-control">
            <option value="kg" selected>kg</option> 
            <option value="g">g</option> 
            <option value="lb">lb</option> 
            <option value="oz">oz</option> 
            <option value="L">L</option> 
            <option value="mL">mL</option> 
            <option value="Tblsp">Tblsp</option> 
            <option value="tsp">tsp</option> 
            <option value="cup">cup</option> 
            <option value="quart">quart</option> 
            <option value="gallon">gallon</option> 
            <option value="package">package</option> 
            <option value="jar">jar</option> 
            <option value="qty">qty</option>
        </select> 
        <div class="input-group-append"> 
            <button class="btn btn-danger" type="button" onclick="remove_ingredient_fields(${uuid});" id="minus-button"> 
                <i class="fa fa-minus-square" aria-hidden="true"></i> 
            </button> 
        </div>
    </div>`
    objTo.appendChild(ingrfield)
}

function remove_ingredient_fields(rid) {
    $('#'+rid).remove();
}
