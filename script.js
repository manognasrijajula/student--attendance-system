const loginButton = document.getElementById("loginBtn");

loginButton.addEventListener("click", function () {

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    if (username === "" || password === "") {
        alert("Please enter username and password");
        return;
    }

    if (username === "admin" && password === "admin123") {
        window.location.href = "dashboard.html";
    } else {
        alert("Invalid username or password");
    }
});