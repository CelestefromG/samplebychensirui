import fs from 'node:fs';
import assert from 'node:assert/strict';
import {ASPECTS,stats,filterReviews,evidence,assemble,validateResult,esc,buildPrompt} from '../docs/core.mjs';
const data=JSON.parse(fs.readFileSync(new URL('../docs/data.json',import.meta.url)));
assert.equal(data.meta.rawRows,2003);assert.equal(data.reviews.length,962);assert.equal(stats(data.reviews).annotations,data.meta.analysis.labels);assert.equal(stats(data.reviews).products,110);
assert.equal(data.reviews.reduce((n,r)=>n+r.sourceRows.length,0),2003);
assert.equal(new Set(data.reviews.map(r=>r.id)).size,962);
for(const category of ['all','Sunscreen','Cleanser','Moisturizer','Serum']){
 const reviews=filterReviews(data.reviews,{category,product:'all'});
 const s=stats(reviews);assert(reviews.length>0);assert.equal(s.annotations,s.aspects.reduce((n,a)=>n+a.positive+a.negative+a.mixed+a.uncertain,0));
 for(const aspect of Object.keys(ASPECTS)){
  const a=s.aspects.find(a=>a.aspect===aspect);
  assert.equal(evidence(reviews,{aspect,tone:'negative',query:''}).length,a.negative);
  assert.equal(evidence(reviews,{aspect,tone:'positive',query:''}).length,a.positive);
  assert.equal(evidence(reviews,{aspect,tone:'all',query:''}).length,a.mentioned);
  for(const t of ['mixed','uncertain'])assert.equal(evidence(reviews,{aspect,tone:t,query:''}).length,a[t]);
  if(a.mentioned){const brief={aspect,brand:'LUMA',facts:'规格 50ml',goal:'促进试用',channel:'抖音'};const result=assemble(reviews,brief);assert.equal(result.plans.length,2);validateResult(result,reviews,brief);assert(buildPrompt(reviews,brief).includes(result.plans[0].evidence_ids[0]));assert(result.plans[0].social.includes('规格 50ml'));}
 }
}
assert.equal(filterReviews(data.reviews,{category:'all',product:'does not exist'}).length,0);
assert.throws(()=>assemble([],{aspect:'greasy'}));
assert.throws(()=>validateResult({insight:'x',plans:[{},{}]},data.reviews,{aspect:'greasy'}));
assert.equal(Object.values(stats(data.reviews).emotions).reduce((a,b)=>a+b,0),962);
for(const r of data.reviews){assert.equal(new Set(r.annotations.map(a=>a.aspect)).size,r.annotations.length);for(const a of r.annotations){for(const q of a.evidence)assert(r.text.includes(q.quote));}}
const bad=assemble(data.reviews,{aspect:'greasy',brand:'x',facts:'',goal:'x',channel:'x'});bad.plans[0].evidence_ids=['R9999'];assert.throws(()=>validateResult(bad,data.reviews,{aspect:'greasy'}));
assert.equal(esc('<img src=x onerror=alert(1)>'),'&lt;img src=x onerror=alert(1)&gt;');
const html=fs.readFileSync(new URL('../docs/index.html',import.meta.url),'utf8'),app=fs.readFileSync(new URL('../docs/app.js',import.meta.url),'utf8');
const ids=new Set([...html.matchAll(/id="([^"]+)"/g)].map(m=>m[1]));
for(const m of app.matchAll(/\$\('([^']+)'\)/g))assert(ids.has(m[1]),'missing element '+m[1]);
console.log('PASS: source reconciliation, all category/aspect statistics, evidence filters, campaign assembly, import rejection, HTML escaping, UI element references');
