function playRound() {
    var input = document.getElementById("userNumber");
    var errorText = document.getElementById("errorText");
    var userNumber = Number(input.value);

    if (input.value === "" || userNumber < 0 || userNumber > 100 || Number.isInteger(userNumber) === false) {
        errorText.innerHTML = "Please enter a whole number between 0 and 100.";
        document.getElementById("resultBox").classList.add("hidden");
        return;
    }

    errorText.innerHTML = "";

    var botNumber = Math.floor(Math.random() * 101);
    var average = (userNumber + botNumber) / 2;
    var spiderNumber = average * 0.8;

    var userDifference = Math.abs(userNumber - spiderNumber);
    var botDifference = Math.abs(botNumber - spiderNumber);

    var winner = "";

    if (userDifference < botDifference) {
        winner = "User";
    } else if (botDifference < userDifference) {
        winner = "Bot";
    } else {
        winner = "Tie";
    }

    document.getElementById("userChoice").innerHTML = userNumber;
    document.getElementById("botChoice").innerHTML = botNumber;
    document.getElementById("averageNumber").innerHTML = average.toFixed(2);
    document.getElementById("targetNumber").innerHTML = spiderNumber.toFixed(2);
    document.getElementById("winnerName").innerHTML = winner;

    document.getElementById("resultBox").classList.remove("hidden");
}
