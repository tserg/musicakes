const page = parseInt(window.appConfig.page.page);

const previousPageButton = document.querySelector('#previous-page-btn');
const nextPageButton = document.querySelector('#next-page-btn');

if (nextPageButton) {

	nextPageButton.addEventListener('click', () => {

		if (page == 0) {

			var next_page = 2;
		}

		else {

			var next_page = page+1;
		}

		window.location.href = "/tracks?page=" + next_page.toString();
	});
}

if (page>1) {

	previousPageButton.addEventListener('click', () => {

		var previous_page = page-1;

		window.location.href = "/tracks?page=" + previous_page.toString();
	});
}

