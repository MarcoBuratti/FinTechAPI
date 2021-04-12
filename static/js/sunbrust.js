import define from "./index.js";


const runtime = new Runtime();
const main = runtime.module(define, Inspector.into(document.body));
