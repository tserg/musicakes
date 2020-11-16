var htmlStyles = window.getComputedStyle(document.querySelector("html"));
var gridRowCount = parseInt(htmlStyles.getPropertyValue("--gridRowNum"));

const releaseCount = parseInt(window.appConfig.release_count.count);

var rowsRequired = Math.ceil(parseFloat(releaseCount)/5);

document.documentElement.style.setProperty("--gridRowNum", rowsRequired);