// Regression for the real message-input pointer resize mapping.
import assert from "node:assert/strict";
import {resizedComposerHeight} from "../../../clients/desktop/dist/desktop/src/ui/composer.js";
assert.equal(resizedComposerHeight(72,100,80),92,"up expands");
assert.equal(resizedComposerHeight(72,100,120),52,"down shrinks");
assert.equal(resizedComposerHeight(72,100,100),72,"stationary is stable");
assert.equal(resizedComposerHeight(72,100,-200),150,"upper bound");
assert.equal(resizedComposerHeight(72,100,400),42,"lower bound");
assert.equal(resizedComposerHeight(150,200,210),140,"can shrink from maximum");
assert.equal(resizedComposerHeight(42,200,190),52,"can expand from minimum");
console.log("PASS composer direction and limits (7 controls)");
