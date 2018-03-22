var mealplan = [];

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
        document.getElementById('descriptionsection' + i).innerHTML = recipedescrip[i];
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