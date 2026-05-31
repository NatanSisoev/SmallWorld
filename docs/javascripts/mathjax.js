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

/* Typeset once the DOM is ready (mkdocs-material document$ hook). With full
 * page reloads (navigation.instant disabled) MathJax v3 auto-typesets on load;
 * this guarded hook is idempotent and harmless. */
document$.subscribe(() => {
  if (window.MathJax && MathJax.typesetPromise) {
    MathJax.typesetPromise();
  }
});
