window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};

/* Re-typeset on each instant-navigation page swap (mkdocs-material). */
document$.subscribe(() => {
  MathJax.startup.promise.then(() => MathJax.typesetPromise());
});
