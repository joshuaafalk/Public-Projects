document.getElementById('file-upload').addEventListener('change', function() {
    if (this.files && this.files.length > 0) {
      var fileName = this.files[0].name;
      document.querySelector('label[for="file-upload"]').textContent = "File uploaded: " + fileName;
      
      document.querySelector('.file-upload-container').style.backgroundColor = '#e0ffe0'; // Light green background for success
    }
});

document.addEventListener('DOMContentLoaded', function() {
    var fileInput = document.getElementById('file-upload');
    var dropContainer = document.querySelector('.file-upload-container');
    var label = document.querySelector('label[for="file-upload"]');
  
    // Highlight drop area when item is dragged over it
    dropContainer.addEventListener('dragover', function(e) {
      e.preventDefault(); 
      dropContainer.classList.add('dragover');
    });
  
    // Remove highlight when dragging leaves the drop area
    dropContainer.addEventListener('dragleave', function(e) {
      dropContainer.classList.remove('dragover');
    });
  
    // Handle file drop
    dropContainer.addEventListener('drop', function(e) {
      e.preventDefault(); 
      dropContainer.classList.remove('dragover');
  
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files; 
        label.textContent = `File Uploaded: ${e.dataTransfer.files[0].name}`;
  
        fileInput.dispatchEvent(new Event('change'));
      }
    });
  

  });
  
