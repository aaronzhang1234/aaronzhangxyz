
function more(){

	var steps = document.getElementById("steps");
	
	var children = steps.childNodes;
	
	var numbered = steps.getElementsByClassName("numbered");
	var length = numbered.length-1;
	
	
	stepnumber = parseInt(numbered[length].innerHTML.replace("Step ",""));
/*	
	for(var i=0;i <numbered.length;i++){
		alert(numbered[i].innerHTML);
	}
*/		
	
	stepnumber++;
	

	var div = document.createElement("div");
	div.className += "col-md-12 form-group";
	
	
	var label=document.createElement("label");
	label.setAttribute("class","numbered");
	var t = document.createTextNode("Step "+stepnumber);
	label.className += " col-md-2 control-label";
	label.append(t);
	
	
	var fileupload = document.createElement("input");
	fileupload.setAttribute("type","file")
	fileupload.setAttribute("name","image"+stepnumber)
	fileupload.className += "col-md-5";
	
	

	
	var recipiestep= document.createElement("textarea");
	recipiestep.setAttribute("name","step"+stepnumber);
	recipiestep.className += "col-md-5";
	var skip = document.createElement("br");
	
	
	
	//var addStep = steps.lastChild;
	//steps.removeChild(steps.lastChild);
	
	div.appendChild(label);
	div.appendChild(recipiestep);
	div.appendChild(fileupload);
	//div.appendChild(addStep);
	
	steps.appendChild(div);
	
}
