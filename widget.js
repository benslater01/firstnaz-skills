/* Temporary forwarder: the sermon notes moved to sermon-notes/widget.js.
   Keeps the old embed working until firstnaz.net points at the new address. Safe to delete after. */
(function () {
  var s = document.currentScript;
  var n = document.createElement("script");
  n.src = s.src.replace(/widget\.js(\?.*)?$/, "sermon-notes/widget.js");
  s.parentNode.insertBefore(n, s.nextSibling);
})();
