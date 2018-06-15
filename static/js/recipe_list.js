var mealplan = [];
var doc = new jsPDF('p', 'pt', [580, 630]);
var count = 0;
var pages = 0;
function deleteRecipe(name)
{
    //deletes recipe
    $.post("/dashboard", {
        name: name,
        func: "del"
        },
        function() {
        location.reload(true);
        });
}

function editRecipe(name)
{
    //edits recipe
    location.href = "/edit_recipe?recipe=" + name;
}

function recipeList()
{
    mealplan = [];
    //shuffle and display list on recipenames side
    var numDays = document.getElementById("sel1").value;
    var objTo = document.getElementById('mealplan');
    while (objTo.firstChild)
    {
        objTo.removeChild(objTo.firstChild);
    }
    for (var i = 0; i < numDays; i++)
    {
        var row = document.createElement("div");
        var namesection = document.createElement("div");
        var descriptionsection = document.createElement("div");
        row.setAttribute("class", "row list-group-item list-group-item-action");
        row.setAttribute("id", "row" + i);
        row.setAttribute("style", "background-color: #F8F8F8;")
        objTo.appendChild(row);
        namesection.setAttribute("class", "col-xs-4");
        namesection.setAttribute("id", "namesection" + i);
        descriptionsection.setAttribute("class", "col-xs-6");
        descriptionsection.setAttribute("id", "descriptionsection" + i);
        row.appendChild(namesection);
        row.appendChild(descriptionsection);
    }
    var stuff = shuffle(recipeBankNames,recipeBankDesc,numDays)
    var recipenames = stuff[0];
    var recipedescrip = stuff[1];

    for (var i = 0; i < numDays; i++)
    {
        document.getElementById('namesection' + i).innerHTML = "Day " + (i + 1) + ":  " + recipenames[i];
        document.getElementById('descriptionsection' + i).innerHTML = recipedescrip[i].slice(0,29);
        mealplan.push(recipenames[i])
    }
}

function shuffle(a,b,count)
{
    var namecopy = a.slice(0);
    var desccopy = b.slice(0);
    var namearray = [];
    var descarray = [];
    for (var i = 0; i < count; i++)
    {
        if (namecopy.length < 1)
        {
            namecopy = a.slice(0);
            desccopy = b.slice(0);
        }
        var index = Math.floor(Math.random() * (namecopy.length - 1));
        namearray.push(namecopy[index]);
        descarray.push(desccopy[index]);
        namecopy.splice(index,1);
        desccopy.splice(index,1);
    }
    return [namearray,descarray];
}
function getList()
{
    console.log(mealplan);
    $.post("/dashboard", {
       namearray: mealplan,
       func: "getList"
    });
}

function reloadPage()
{
    window.location.reload(true);
}

function createListPage(count)
{
    var container = document.createElement('div');
    container.setAttribute('id', 'shoppinglistcontainer' + count);
    container.setAttribute('class', 'container');
    container.setAttribute('style', 'background-color:#ffffff; width:155mm');

    var tablecontainer = document.createElement('div');
    tablecontainer.setAttribute('id', 'shoppingtabledata' + count);
    tablecontainer.setAttribute('class', 'card mx-auto border-dark mb-3 text-center small');
    tablecontainer.setAttribute('style', 'padding:1em;');

    var title = document.createElement('h5');
    title.setAttribute('class', 'card-title');
    title.innerText = 'Shopping List Page ' + count;

    var table = document.createElement('table');
    table.setAttribute('id', 'page' + count);
    table.setAttribute('class', 'table');

    var tablehead = document.createElement('thead');
    var tablerow = document.createElement('tr');

    var col1 = document.createElement('th');
    col1.setAttribute('scope', 'col');
    col1.innerText = '#';

    var col2 = document.createElement('th');
    col2.setAttribute('scope', 'col');
    col2.innerText = 'Name';

    var col3 = document.createElement('th');
    col3.setAttribute('scope', 'col');
    col3.innerText = 'Amount';

    var col4 = document.createElement('th');
    col4.setAttribute('scope', 'col');
    col4.innerText = 'Unit';

    var tbody = document.createElement('tbody');
    tbody.setAttribute('id', 'tablebody' + count);

    tablerow.appendChild(col1);
    tablerow.appendChild(col2);
    tablerow.appendChild(col3);
    tablerow.appendChild(col4);
    tablehead.appendChild(tablerow);
    table.appendChild(tablehead);
    table.appendChild(tbody);
    tablecontainer.appendChild(title);
    tablecontainer.appendChild(table);
    container.appendChild(tablecontainer);
    document.body.appendChild(container);
}

function createList()
{
    var recipes = JSON.parse(recipedict);
    var ingredients = [];
    var amounts = [];
    var units = [];
    var newingredients = [];
    var newamounts = [];
    var newunits = [];


    if (mealplan.length != 0)
    {
        for (var i = 0; i < mealplan.length; i++)
        {
            for (var j = 0; j < recipes[mealplan[i]][0].length; j++)
            {
                ingredients.push(recipes[mealplan[i]][0][j]);
            }
            for (var j = 0; j < recipes[mealplan[i]][1].length; j++)
            {
                amounts.push(parseFloat(recipes[mealplan[i]][1][j]));
            }
            for (var j = 0; j < recipes[mealplan[i]][2].length; j++)
            {
                units.push(recipes[mealplan[i]][2][j]);
            }
        }
        for (var i = 0; i < ingredients.length; i++)
        {
            var switchy = 1;
            for(var j = 0, k = newingredients.length; j < k; j++)
            {
                if (ingredients[i] === newingredients[j] && units[i] === newunits[j])
                {
                    // duplicate value
                    newamounts[j] = amounts[i] + newamounts[j];
                    switchy = 0;
                }

            }
            console.log(switchy);
            if (switchy === 1)
            {
                newingredients.push(ingredients[i]);
                newamounts.push(amounts[i]);
                newunits.push(units[i]);
            }

        }

        // create first table
        var numberofpages = 0;
        numberofpages += Math.floor(newingredients.length/11);
        if (newingredients.length % 11)
        {
            numberofpages += 1;
        }
        pages = numberofpages;
        for (var i = 0; i < numberofpages; i++)
        {
            createListPage(i+1);
        }
        var pagecount = 1;
        for (var i = 0; i < newingredients.length; i++)
        {
            if ((i+1) % 11 === 0)
            {
                pagecount += 1;
            }
            var tablerow = document.createElement('tr');
            tablerow.setAttribute('id', 'ingredient' + i);
            var tablehead = document.createElement('th');
            tablehead.setAttribute("scope", "row");
            tablehead.innerText = i + 1;
            var ingredientname = document.createElement('td');
            ingredientname.innerText = newingredients[i];
            var amount = document.createElement('td');
            amount.innerText = newamounts[i];
            var unit = document.createElement('td');
            unit.innerText = newunits[i];
            tablerow.appendChild(tablehead);
            tablerow.appendChild(ingredientname);
            tablerow.appendChild(amount);
            tablerow.appendChild(unit);
            var tbody = document.getElementById('tablebody' + pagecount);
            tbody.appendChild(tablerow);
        }


        for (var i = 0; i < numberofpages; i++)
        {
            var container = document.getElementById('shoppinglistcontainer' + (i + 1));
            html2canvas(container, {
                onrendered: function(canvas) {
                    //canvas.setAttribute('id', 'shoppinglistcanvas' + (i + 1));
                    //document.body.appendChild(canvas);
                    var imgdata = canvas.toDataURL("image/jpeg", 0.75);
                    console.log(imgdata);
                    var width = canvas.width;
                    var height = canvas.height;
                    doc.addImage(imgdata, 'PNG', 20, 20, (width - 40), (height-40));
                    if (count < pages - 1)
                    {
                        doc.addPage();
                    }
                    count++;
                }
            });
        }
        setTimeout(function(){
            doc.save('ShoppingList.pdf');
        },1);
    }
}
