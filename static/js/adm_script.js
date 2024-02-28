function closeSidebar() {
    document.getElementById('sidebar').classList.remove('active');
}

document.getElementById('sidebar-toggle').addEventListener('click', function () {
    document.getElementById('sidebar').classList.toggle('active');
});

setTimeout(function() {
    var flashMessage = document.getElementById('flash-message');
    if (flashMessage) {
      flashMessage.style.display = 'none';
    }
}, 2000);