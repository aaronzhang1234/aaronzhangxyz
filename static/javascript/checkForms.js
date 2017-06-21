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
		alert("you have to click the checkbox")
		errors=true;
	}
	
	
	
	
	
	if(errors){
		event.preventDefault();
	}
	
}
function checkAddRecipe(form){
	var errors = false;
	/*
	if(/\s/.test(form.recipiename.value)||form.recipiename.value == ""){
		form.recipiename.style.backgroundColor="red";
		form.recipiename.style.color="white";
		errors=true;
	}
	else{
		form.recipiename.style.backgroundColor="white";
		form.recipiename.style.color="black";
	}
	
	if(/\s/.test(form.recipiename.value)||form.step1.value=""){
		form.step1.style.backgroundColor="red";
		form.step1.style.color="white";
		errors=true;
	}
	else{
		form.step1.style.backgroundColor="white";
		form.step1.style.color="black";
	}
	*/
	if(errors){
		event.preventDefault();
	}
	

	
}