function delete_user(id) {
    document.getElementById('user_id').value = id;
}

function edit_user(user_id, is_admin, is_superuser) {
    document.getElementById('edit_id').value = user_id;
    // document.getElementById('edit_first_name').value = first_name;
    // document.getElementById('edit_last_name').value = last_name;
    if (is_admin === "True") {
        document.getElementById('edit_admin').checked = true;
    }
    if (is_superuser === "True") {
        document.getElementById('edit_superuser').checked = true;
    }

    $("#edit_button").trigger('click');

}