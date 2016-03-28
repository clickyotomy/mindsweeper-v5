get_leaderboard = function(){
  $.ajax({
    url: "/leaderboard",
    success: function(data) {
    //   console.log(data["leaderboard"]);
      jQuery('#live-leaderboard').html('');
      var leaderboard = $("#live-leaderboard");
      var table = document.createElement('TABLE');
      var tableBody = document.createElement('TBODY');
      table.appendChild(tableBody);
      for(var i = 0; i < data["leaderboard"].length; i++) {
        var tr = document.createElement('TR');
        if(data["leaderboard"][i][0] == $("#hidden-current-user").text()) {
          tr.className = "current-user";
        }
        tableBody.appendChild(tr);
        var rank_td = document.createElement('TD');
        rank_td.appendChild(document.createTextNode(i+1));
        tr.appendChild(rank_td);
        var name_td = document.createElement('TD');
        name_td.appendChild(document.createTextNode(data["leaderboard"][i][0]));
        tr.appendChild(name_td);
        var level_td = document.createElement('TD');
        level_td.appendChild(document.createTextNode(data["leaderboard"][i][data["leaderboard"][i].length - 1]));
        tr.appendChild(level_td);
      }
      table.appendChild(tableBody);
      leaderboard.append(table);
    },
    complete: function() {
      setTimeout(get_leaderboard, 30000);
    }
  });
}
