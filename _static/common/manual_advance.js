// only player one asks for advance periodically
if (js_vars.player_id === 1) {
    window.setInterval(function () {
        liveSend('advance?')
    }, 5000);
} else {
    // we need to ask at least once in case player 1 is gone and in case that we arrived late to the waitpage
    liveSend('advance?')
}

function liveRecv(data) {
    if (data['advance'] === js_vars.current_page_name) {
        document.getElementById('form').submit();
    }
}
