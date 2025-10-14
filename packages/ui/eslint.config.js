import js from "@eslint/js";

export default [
  js.configs.recommended,
  {
    files: ["**/*.{ts,tsx}"],
    ignores: ["dist/**", "node_modules/**"],
    rules: {
      "no-unused-vars": "warn",
    },
  },
];
