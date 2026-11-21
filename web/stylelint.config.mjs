// Enforces the AGENTS.md token rules in CSS. Raw values live only in the global
// token files; everything else references var(--token).
const LENGTH_UNITS = ["px", "rem", "em"];
const BORDER_PROPERTY = /^border(-(top|right|bottom|left|block|inline)(-(start|end))?)?(-(width|style))?$/;
// Relative colors derived from a token (`oklch(from var(--x) l c h / 0.5)`) are not raw values.
const RAW_COLOR_FUNCTION = "/\\b(rgba?|hsla?|hwb|lab|lch|oklab|oklch)\\((?!\\s*from\\s+var\\()/";
const VISIBLE_BORDER = "/^(?!(none|0)$).+/";

/** @type {import("stylelint").Config} */
const config = {
  rules: {
    "color-no-hex": true,
    // Masks read only alpha, so `linear-gradient(black, black)` names no visible color.
    "color-named": ["never", { ignoreProperties: ["/^(-webkit-)?mask/"] }],
    // Media queries cannot read var(), so breakpoints stay in px.
    "unit-disallowed-list": ["px", { ignoreMediaFeatureNames: { px: ["/width$/", "/height$/"] } }],
    // Text color only from text tokens (alpha white/black, --text-* in app/globals.css),
    // or ink derived from a token (contrast snap on a data-colored background).
    "declaration-property-value-allowed-list": {
      color: ["/^var\\(--text-[a-z-]+\\)$/", "/^oklch\\(\\s*from\\s+var\\(/", "inherit", "currentColor", "transparent"],
    },
    // Raw color functions fail; visible borders only warn (taste, not a hard rule). `none` / `0` pass.
    "declaration-property-value-disallowed-list": [
      { [`/${BORDER_PROPERTY.source}/`]: [VISIBLE_BORDER], "/.*/": [RAW_COLOR_FUNCTION] },
      {
        severity: (property) => (BORDER_PROPERTY.test(property) ? "warning" : "error"),
        message: (property, value) =>
          BORDER_PROPERTY.test(property)
            ? "Avoid borders: separate with spacing or background contrast instead."
            : `No raw color function in "${value}". Use var(--token) or oklch(from var(--token) ...).`,
      },
    ],
    // letter-spacing stays free: tracking in em scales with the font, as it should.
    "declaration-property-unit-disallowed-list": {
      "/^(margin|padding|gap|row-gap|column-gap|inset|top|right|bottom|left)/": LENGTH_UNITS,
      "/^(font-size|line-height|border-radius)$/": LENGTH_UNITS,
    },
  },
  overrides: [
    {
      files: ["app/globals.css"],
      rules: {
        "color-no-hex": null,
        "unit-disallowed-list": null,
        "declaration-property-unit-disallowed-list": null,
        "declaration-property-value-disallowed-list": [
          { [`/${BORDER_PROPERTY.source}/`]: [VISIBLE_BORDER] },
          { severity: "warning", message: "Avoid borders: separate with spacing or background contrast instead." },
        ],
      },
    },
  ],
};

export default config;
