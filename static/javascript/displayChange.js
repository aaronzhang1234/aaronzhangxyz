window.onload = function()
{
	var changeAccountBtn = document.getElementById("changeAccount");
	var changeAccountForm = document.getElementById("changeAccountForm");
	var closeAccountBtn = document.getElementById("closeAccountBtn");
    var deleteAccountBtn = document.getElementById("deleteAccount");
	// Shows Form on click
	changeAccountBtn.onclick = function()
	{
		changeAccountForm.classList.remove("hidden");
        deleteAccountBtn.classList.remove("hidden");
		changeAccountBtn.className += " hidden";
        
	}

	// Hides form on click
	closeAccountBtn.onclick = function()
	{
		changeAccountBtn.classList.remove("hidden");
		changeAccountForm.className += " hidden";
        deleteAccountBtn.classList += " hidden";
	
	}
}