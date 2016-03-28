/*
    Source: http://stackoverflow.com/questions/9335140/how-to-countdown-to-a-date
*/

function CountDownTimer(dt, id)
{
    var end = new Date(dt);

    var _second = 1000;
    var _minute = _second * 60;
    var _hour = _minute * 60;
    var _day = _hour * 24;
    var timer;

    function showRemaining() {
        var now = new Date();
        var distance = end - now;

        if (distance < 0) {
            clearInterval(timer);
            document.getElementsByClassName(id)[0].innerHTML = 'Start playing!';
            location.reload(true)
            return;
        }

        var days = Math.floor(distance / _day);
        var hours = Math.floor((distance % _day) / _hour);
        var minutes = Math.floor((distance % _hour) / _minute);
        var seconds = Math.floor((distance % _minute) / _second);

        document.getElementsByClassName(id)[0].innerHTML = days + ' days, ';
        document.getElementsByClassName(id)[0].innerHTML += hours + ' hr - ';
        document.getElementsByClassName(id)[0].innerHTML += minutes + ' min - ';
        document.getElementsByClassName(id)[0].innerHTML += seconds + ' sec';
    }

    timer = setInterval(showRemaining, 1000);
}
