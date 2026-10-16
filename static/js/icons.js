const svg = (d, cls = "") => `<svg ${cls && `class="${cls}" `}viewBox="0 0 24 24" aria-hidden="true">${d}</svg>`;

export const IC = {
  expand: svg('<path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>'),
  shrink: svg('<path d="M4 14h6v6M20 10h-6V4M14 10l7-7M3 21l7-7"/>'),
  chev: svg('<path d="m6 9 6 6 6-6"/>', "chev"),
  dl: svg('<path d="M12 3v12m0 0-4-4m4 4 4-4M4 21h16"/>'),
  cal: svg('<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/>'),
  plus: svg('<path d="M12 5v14M5 12h14"/>'),
  izq: svg('<path d="m15 18-6-6 6-6"/>'),
  der: svg('<path d="m9 18 6-6-6-6"/>'),
  tema: svg('<circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/>'),
  vista: svg('<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>'),
};
