window.onload = function()
{
	var manageGroupBtn =   document.getElementById("manageGroupBtn");
	var manageGroupForm =  document.getElementById("managegroup");
	var closeManageGroup = document.getElementById("closeManageGroup");
	var deleteAccount =    document.getElementById("deletegroupBtn");

	// Shows Form on click
	manageGroupBtn.onclick = function()
	{
		manageGroupForm.classList.remove("hidden");
		deleteAccount.classList.remove("hidden");
		manageGroupBtn.className += " hidden";
	}

	// Hides form on click
	closeManageGroup.onclick = function()
	{
		manageGroupBtn.classList.remove("hidden");
		manageGroupForm.className += " hidden";	
		deleteAccount.className += " hidden";
	}
}