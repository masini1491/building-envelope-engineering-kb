import assert from 'node:assert/strict';
import {evaluate,compare} from './math.mjs';
import {FIXED_SYNTHETIC as evidence} from './fixtures.mjs';
const A={length:1200,width:300,plateThickness:3,ribWidth:50,ribHeight:50,ribThickness:3,ribCount:1};
const B={...A,ribHeight:60};
assert.equal(evaluate(A).plateVolumeMm3,1080000);
assert.equal(evaluate(A).ribAreaMm2,432);
assert.equal(evaluate(A).ribsVolumeMm3,518400);
assert.equal(evaluate(A).totalVolumeCm3,1598.4);
assert.equal(evaluate({...A,ribCount:0}).ribsVolumeMm3,0);
assert.equal(evaluate({...A,ribCount:2}).ribsVolumeMm3,1036800);
assert.equal(compare(A,A).deltaPercent,0);
assert.ok(compare(A,B).deltaPercent>0);
assert.equal(compare(A,B).deltaCm3,72);
for(const invalid of [{...A,ribWidth:6},{...A,ribHeight:3},{...A,length:0},
                       {...A,plateThickness:300},{...A,ribCount:-1},{...A,ribCount:0.5},
                       {...A,ribThickness:Infinity},{...A,ribThickness:NaN},
                       {...A,ribCount:101}]) {
 assert.throws(()=>evaluate(invalid),RangeError);
}
assert.deepEqual(evidence.ribHeightsMm,[0,4,8]);
assert.deepEqual(evidence.centerDeflectionMm,[0.0002382199,0.0001840568,0.0001079533]);
assert.ok(evidence.centerDeflectionMm.every((v,i,all)=>i===0||v<all[i-1]));
assert.equal(evidence.engineeringAcceptance,'NOT_ADMITTED');
console.log('research-only site contract tests PASS');
