function checkCreateAccount(form){
	
	var errors = false;
	
	if(!(form.password1.value==form.password2.value)||form.password1.value==""){
		
		alert("Passwords must be the same");
		
		form.password1.style.backgroundColor='red';
		form.password1.style.color = 'white';
		
		form.password2.style.backgroundColor="red";
		form.password2.style.color = 'white';
		errors=true;
	}
	else{
		
		form.password1.style.backgroundColor='white';
		form.password1.style.color='black';
		
		form.password2.style.backgroundColor='white';
		form.password2.style.color='black';
	}
	
	if(/\s/.test(form.username.value) ||form.username.value ==""){
		form.username.style.backgroundColor="red";
		form.username.style.color='white';
		errors=true;
	}
	else{
		form.username.style.backgroundColor="white";
		form.username.style.color="black";
	}
	
	if(form.privacy.checked == false){
		alert("you have to click the checkbox");
		errors=true;
	}
	if(errors){
		event.preventDefault();
	}
	
}
function checkAddRecipe(form){
	var errors = false;
	if(form.recipename.value == ""){
        alert("Recipename cannot be blank");
		form.recipename.style.backgroundColor="red";
		form.recipename.style.color="white";
		errors=true;
	}
	else{
		form.recipename.style.backgroundColor="white";
		form.recipename.style.color="black";
	}
    
    textareas = form.getElementsByTagName('textarea');
    if(textareas[0].value==""){
        alert("Description cannot be blank");
        errors=true;
    }
    for(i = 1; i<textareas.length; i++){
        if(textareas[i].value==""){
            alert("Step "+i+" cannot be blank");
            errors=true;   
        }
    }

	if(form.step1.value==""){
        alert("Step 1 cannot be blank");
		form.step1.style.backgroundColor="red";
		form.step1.style.color="white";
		errors=true;
	}
	else{
		form.step1.style.backgroundColor="white";
		form.step1.style.color="black";
	} 
	
	if(errors){
		event.preventDefault();
	}
}
function checkCreateGroup(form){
    var errors = false;
    var groupname = form.groupname.value;

    if(groupname.length >20 || groupname==""){
        alert("Group Names can only be between 1 and 20 characters");
        form.groupname.style.backgroundColor = "red";
        form.groupname.style.color = "white";
        errors = true;
    }
    else{
        form.groupname.style.backgroundColor = "white";
        form.groupname.style.color = "black";
    }

    if(errors){
        event.preventDefault();
    }
}
