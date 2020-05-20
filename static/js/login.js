function checkForm(form)
  {
    if(form.username.value == "") {
      alert("Error: Username cannot be blank!");
      form.username.focus();
      return false;
    }
    if(form.password.value == "") {
        alert("Error: Password cannot be blank!");
        form.password.focus();
        return false;
      }
    return true;
  }