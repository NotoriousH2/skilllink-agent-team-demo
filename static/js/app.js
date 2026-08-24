document.addEventListener("DOMContentLoaded", function () {
  var forms = document.querySelectorAll("form[data-confirm]");
  forms.forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!window.confirm(form.getAttribute("data-confirm"))) {
        e.preventDefault();
      }
    });
  });
});
