export interface Appearance {theme:"cold"|"warm";fontSize:14|16|18|20;density:"compact"|"comfortable"|"spacious"}
const APPEARANCE_KEY = "plugworldim.appearance.v1";
export const defaults:Appearance={theme:"cold",fontSize:16,density:"comfortable"};
export function validate(value:unknown):Appearance {
  if(!value||typeof value!=="object"||Array.isArray(value))throw new Error("Invalid appearance");
  const v=value as Record<string,unknown>;
  if(Object.keys(v).length!==3||!['theme','fontSize','density'].every(k=>Object.hasOwn(v,k))||typeof v.theme!=="string"||!['cold','warm'].includes(v.theme)||typeof v.fontSize!=="number"||![14,16,18,20].includes(v.fontSize)||typeof v.density!=="string"||!['compact','comfortable','spacious'].includes(v.density))throw new Error("Invalid appearance");
  return {theme:v.theme as Appearance['theme'],fontSize:v.fontSize as Appearance['fontSize'],density:v.density as Appearance['density']};
}
export function loadAppearance():Appearance {
  try {const raw=window.localStorage.getItem(APPEARANCE_KEY);if(!raw||raw.length>128)return {...defaults};return validate(JSON.parse(raw));}catch{return {...defaults};}
}
export function saveAppearance(value:Appearance):boolean {
  const valid=validate(value);
  try {window.localStorage.setItem(APPEARANCE_KEY, JSON.stringify({theme: valid.theme, fontSize: valid.fontSize, density: valid.density}));return true;}catch{return false;}
}
