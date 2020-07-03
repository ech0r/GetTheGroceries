var mealplan = [];
var descriptions = [];
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
        row.setAttribute("class", "list-group-item");
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
    descriptions = stuff[1];

    for (var i = 0; i < numDays; i++)
    {
        document.getElementById('namesection' + i).innerHTML = "Day " + (i + 1) + ":  " + recipenames[i];
        document.getElementById('descriptionsection' + i).innerHTML = recipedescrip[i].slice(0,29);
        mealplan.push(recipenames[i])
    }
    window.location.hash = '#mealplan'
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

function tablebody(ingredients, amounts, units)
{
    var body = [];
    var header = [{text: '#',style: 'tableHeader'},{text: 'Name', style: 'tableHeader'},{text: 'Amount', style: 'tableHeader'},{text: 'Unit', style: 'tableHeader'}];
    body.push(header);
    for (var i = 0; i < ingredients.length; i++)
    {
        var row = [];
        row.push({text: i+1});
        row.push({text: ingredients[i]});
        row.push({text: amounts[i]});
        row.push({text: units[i]});
        body.push(row);
    }
    return body;
}

function mealplantable()
{
    var body = [];
    var header = [{text: 'Day #', style: 'tableHeader'}, {text: 'Recipe', style: 'tableHeader'}, {text: 'Description', style: 'tableHeader'}];
    body.push(header);
    for (var i = 0; i < mealplan.length; i++) {
        var row = [];
        row.push({text: i + 1});
        row.push({text: mealplan[i]});
        row.push({text: descriptions[i]});
        body.push(row);
    }
    return body;
}

function createList()
{
    var recipes = JSON.parse(recipedict);
    console.log(mealplan);
    var ingredients = [];
    var amounts = [];
    var units = [];
    var newingredients = [];
    var newamounts = [];
    var newunits = [];


    if (mealplan.length != 0) {
        for (var i = 0; i < mealplan.length; i++) {
            for (var j = 0; j < recipes[mealplan[i]][0].length; j++) {
                ingredients.push(recipes[mealplan[i]][0][j]);
            }
            for (var j = 0; j < recipes[mealplan[i]][1].length; j++) {
                amounts.push(parseFloat(recipes[mealplan[i]][1][j]));
            }
            for (var j = 0; j < recipes[mealplan[i]][2].length; j++) {
                units.push(recipes[mealplan[i]][2][j]);
            }
        }
        for (var i = 0; i < ingredients.length; i++) {
            var switchy = 1;
            for (var j = 0, k = newingredients.length; j < k; j++) {
                if (ingredients[i] === newingredients[j] && units[i] === newunits[j]) {
                    // duplicate value
                    newamounts[j] = amounts[i] + newamounts[j];
                    switchy = 0;
                }

            }
            console.log(switchy);
            if (switchy === 1) {
                newingredients.push(ingredients[i]);
                newamounts.push(amounts[i]);
                newunits.push(units[i]);
            }

        }

        var body = tablebody(newingredients, newamounts, newunits);
        var mealplanbody = mealplantable();
        var docDefinition = {
            pageMargins: [40, 60, 40, 60],
            pageSize: 'A4',
            content: [
                {
                    image: 'data:image/png;base64,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',
                    fit: [500, 2000]
                },
                {text: 'Meal Plan', style: 'subheader'},
                {
                    table: {
                        widths: ['*', '*', '*'],
                        headerRows: 1,
                        body: mealplanbody
                    }
                },

                {text: 'Shopping List', style: 'subheader'},
                {
                    table: {
                        widths: ['*', '*', '*', 'auto'],
                        headerRows: 1,
                        body: body
                    }
                },
            ],
            styles: {
		        header: {
			    fontSize: 18,
			    bold: true,
			    margin: [0, 0, 0, 10]
		    },
            subheader: {
			    fontSize: 16,
			    bold: true,
			    margin: [0, 10, 0, 5]
		    },
		    tableExample: {
			    margin: [0, 5, 0, 15]
		    },
		    tableHeader: {
			    bold: true,
			    fontSize: 13,
			    color: 'black'
		    }
	    }
        };
        var today = new Date();
        var day = today.getDate();
        var month = today.getMonth() + 1;
        var year = today.getFullYear();
        var date = day + "-" + month + "-" + year;
        pdfMake.createPdf(docDefinition).download("shoppinglist" + "-" + date + ".pdf");
    }
};
