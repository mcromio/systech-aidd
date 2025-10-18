// Utility функции

export function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(cls => typeof cls === "string").join(" ");
}
