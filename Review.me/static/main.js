function toggleFilters(search) {
    usernameFilter = false;
    titleFilter = false;
    tagFilter = false;
    
    usernameFilter = document.getElementById("usernameFilter").checked;
    titleFilter = document.getElementById("titleFilter").checked;
    tagFilter = document.getElementById("tagFilter").checked;
    search = document.getElementById("searchPhrase").textContent;
    
    window.location.href = "/search_results?usernameFilter=" + usernameFilter.toString() +
        "&titleFilter=" + titleFilter.toString() + "&tagFilter=" + tagFilter.toString() + 
        "&search=" + search.toString();
}

function editComment(comment, comment_id) {
    document.getElementById("addCommentText").value = comment
    document.getElementById("commentSubmit").action = "/editComment?comment_id=" + comment_id
}

var loadFile = function(event) {
    var output = document.getElementById('pfp_preview');
    output.src = URL.createObjectURL(event.target.files[0]);
    output.onload = function() {
      URL.revokeObjectURL(output.src) // free memory
    }
  };

