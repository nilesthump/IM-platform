// Copy approved runtime distributions and static assets; no bundler/runtime.
// Explicit Node standard library for build-time copies; never a guest runtime.
const {mkdir,copyFile,cp}=process.getBuiltinModule("fs").promises;
await mkdir("dist/vendor",{recursive:true});
for(const name of ["index.html","style.css"])await copyFile("src/ui/"+name,"dist/"+name);
for(const name of ["react","react-dom"])await copyFile("src/ui/"+name+".config.mjs","dist/"+name+".mjs");
await copyFile("node_modules/react/umd/react.production.min.js","dist/vendor/react.js");
await copyFile("node_modules/react-dom/umd/react-dom.production.min.js","dist/vendor/react-dom.js");
await cp("node_modules/@tauri-apps/api","dist/vendor/tauri",{recursive:true});
