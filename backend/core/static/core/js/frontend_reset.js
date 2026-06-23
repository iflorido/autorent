// Botones "Restablecer" del admin de FrontendConfig.
// Cada botón pone el valor por defecto (data-default) en su input asociado.
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".ar-reset").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var wrapper = btn.closest("div");
      var input = wrapper ? wrapper.querySelector("input[type=text]") : null;
      if (input) {
        input.value = btn.getAttribute("data-default");
        input.dispatchEvent(new Event("change", { bubbles: true }));
      }
    });
  });
});