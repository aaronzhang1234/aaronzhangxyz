window.onload = function()
{
	var btnShowReview = document.getElementById("writeReviewBtn");
	var writeReviewForm = document.getElementById("writeReview");
	var btnHideReview = document.getElementById("closeWriteReview");

	// Shows Form on click
	btnShowReview.onclick = function()
	{
		writeReviewForm.classList.remove("hidden");
		btnShowReview.className += " hidden";
	}

	// Hides form on click
	btnHideReview.onclick = function()
	{
		btnShowReview.classList.remove("hidden");
		writeReviewForm.className += " hidden";	
	}
}