function toggleForm(form) {
    if (form === 'create') {
        document.getElementById('login-content').style.display = 'none';
        document.getElementById('create-content').style.display = 'block';
    } else {
        document.getElementById('login-content').style.display = 'block';
        document.getElementById('create-content').style.display = 'none';
    }
}