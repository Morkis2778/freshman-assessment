// Executes the delivered inline JS in Node with a minimal DOM/canvas harness.
// This verifies game rules and state persistence, not visual browser rendering.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'game/snake.html'),'utf8');
const data=new Map(),elements=new Map();let interval=null;
function element(){return {textContent:'',value:'90',dataset:{},classList:{toggle(){}},append(){},replaceChildren(){},getContext(){return new Proxy({},{get:(o,k)=>o[k]||(()=>{}),set:(o,k,v)=>(o[k]=v,true)})},addEventListener(){},setPointerCapture(){}}}
const ctx={console,Math:Object.create(Math),Date,Map,Set,Number,JSON,document:{getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},body:element(),createElement:element,querySelectorAll:()=>[],addEventListener(){}},localStorage:{getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v)},setInterval(fn){interval=fn;return 1},clearInterval(){interval=null},confirm:()=>true,window:{}};
vm.createContext(ctx);vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],ctx);
const run=s=>vm.runInContext(s,ctx);
const records=[];
for(let seed=1;seed<=100;seed++){
 let rng=seed;ctx.Math.random=()=>{rng=(1664525*rng+1013904223)>>>0;return rng/2**32};
 run("newGame('AI');clearInterval(timer);for(let i=0;i<2161&&running;i++)step();");
 const snapshot=ctx.window.snakeSnapshot();assert.equal(snapshot.score,15);assert.equal(snapshot.running,false);assert.equal(snapshot.saved.history[0].result,'验收通过');records.push({seed,score:snapshot.score,steps:snapshot.steps});
}
assert.equal(run("new Set(cycle.map(q=>q.x+','+q.y)).size"),144);
assert(run('cycle.every((a,i)=>{const b=cycle[(i+1)%cycle.length];return Math.abs(a.x-b.x)+Math.abs(a.y-b.y)===1})'));
run("newGame('手动');clearInterval(timer);turn(-1,0);step();");assert.equal(run('snake[0].x'),3);
run('pause()');const before=run('JSON.stringify(snake)');run('step()');assert.equal(run('JSON.stringify(snake)'),before);run('pause();while(running)step()');assert.equal(run('saved.history[0].result'),'失败');
run("newGame('手动');clearInterval(timer);snake=[{x:3,y:3},{x:3,y:4},{x:4,y:4},{x:4,y:3},{x:4,y:2}];dir={x:0,y:-1};pending={x:1,y:0};food={x:8,y:8};step()");assert.equal(run('running'),false);
run("newGame('手动');clearInterval(timer);snake=[{x:1,y:1},{x:1,y:2},{x:2,y:2},{x:2,y:1}];dir={x:0,y:-1};pending={x:1,y:0};food={x:8,y:8};step()");assert.equal(run('running'),true);
run("newGame('手动');clearInterval(timer);snake=cycle.slice(1).reverse().map(q=>({...q}));food={...cycle[0]};dir={x:0,y:-1};pending={x:0,y:-1};step()");assert.equal(run('saved.history[0].result'),'通关');
run("newGame('手动');clearInterval(timer);food={x:3,y:0};step()");assert.equal(run('score'),1);assert.equal(run('snake.length'),4);
// The actual setInterval callback must autonomously progress the AI.
run("newGame('AI')");const tick=interval;for(let i=0;i<2161&&run('running');i++)tick();assert.equal(run('score'),15);
run("saved.theme='light';persist()");assert.equal(JSON.parse(data.get('freshman-snake-v1')).theme,'light');assert.equal(run('saved.history.length'),10);
ctx.document.getElementById('reset').onclick();assert.equal(run('saved.games'),0);assert.equal(run('saved.best'),0);assert.equal(run('saved.history.length'),0);
const result={status:'PASS',environment:'Node.js VM executes unmodified delivered inline JS with DOM/canvas stubs',ai_random_runs:100,food_each_run:15,min_steps:Math.min(...records.map(r=>r.steps)),max_steps:Math.max(...records.map(r=>r.steps)),cycle_cells:144,checks:['cycle coverage and adjacency','reverse prevention','pause','wall collision','self collision','vacating tail is safe','full-board victory','food growth','timer callback automatic run','persisted theme JSON','last 10 records','reset'],browser_visual_test:'NOT RUN: local Chromium startup blocked by environment socket restrictions; run test_game.py locally',records};
fs.writeFileSync(path.join(root,'tests/game_logic_results.json'),JSON.stringify(result,null,2));console.log(JSON.stringify({...result,records:undefined},null,2));
