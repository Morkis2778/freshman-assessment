"""Optional acceptance: pip install playwright; python -m playwright install chromium.
CHROME_PATH may select an already-installed Chrome executable.
"""
import os,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as p:
    options={'headless':True,'args':['--no-sandbox']}
    if os.environ.get('CHROME_PATH'):options['executable_path']=os.environ['CHROME_PATH']
    browser=p.chromium.launch(**options)
    page=browser.new_page(viewport={'width':1100,'height':900})
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto((ROOT/'game/snake.html').as_uri())
    result=page.evaluate('''() => {
      const records=[]; const nativeRandom=Math.random;
      for(let seed=1;seed<=100;seed++){
        let state=seed;Math.random=()=>{state=(1664525*state+1013904223)>>>0;return state/4294967296;};
        newGame('AI');clearInterval(timer);
        for(let i=0;i<15*144+1&&running;i++)step();
        if(score!==15||running||saved.history[0].result!=='验收通过')throw Error('AI failed seed '+seed);
        records.push({seed,score,steps});
      }
      Math.random=nativeRandom;
      const coords=new Set(cycle.map(q=>q.x+','+q.y));
      if(coords.size!==144)throw Error('cycle duplicate');
      for(let i=0;i<144;i++){const a=cycle[i],b=cycle[(i+1)%144];if(Math.abs(a.x-b.x)+Math.abs(a.y-b.y)!==1)throw Error('cycle gap');}
      newGame('手动');clearInterval(timer);turn(-1,0);step();if(snake[0].x!==3)throw Error('reverse accepted');
      pause();const before=JSON.stringify(snake);step();if(JSON.stringify(snake)!==before)throw Error('pause failed');pause();
      while(running)step();if(saved.history[0].result!=='失败')throw Error('wall collision missing');
      newGame('手动');clearInterval(timer);snake=[{x:3,y:3},{x:3,y:4},{x:4,y:4},{x:4,y:3},{x:4,y:2}];dir={x:0,y:-1};pending={x:1,y:0};food={x:8,y:8};step();if(running)throw Error('self collision missing');
      newGame('手动');clearInterval(timer);snake=[{x:1,y:1},{x:1,y:2},{x:2,y:2},{x:2,y:1}];dir={x:0,y:-1};pending={x:1,y:0};food={x:8,y:8};step();if(!running)throw Error('tail move rejected');
      newGame('手动');clearInterval(timer);snake=cycle.slice(1).reverse().map(q=>({...q}));food={...cycle[0]};dir={x:0,y:-1};pending={x:0,y:-1};step();if(running||saved.history[0].result!=='通关')throw Error('full board win missing');
      newGame('手动');clearInterval(timer);food={x:3,y:0};step();if(score!==1||snake.length!==4)throw Error('food growth missing');
      saved.theme='light';persist();render();
      return {ai_random_runs:records.length,min_steps:Math.min(...records.map(r=>r.steps)),max_steps:Math.max(...records.map(r=>r.steps)),all_score:15,cycle_unique_cells:coords.size,manual_checks:['reverse','pause','wall','self collision','vacating tail','full board win','food growth'],records};
    }''')
    page.reload();assert page.locator('body').evaluate("e=>e.classList.contains('light')")
    assert page.evaluate('snakeSnapshot().saved.history.length')==10
    page.locator('#theme').click();page.reload();assert not page.locator('body').evaluate("e=>e.classList.contains('light')")
    # Drive the actual interval with browser virtual time, without calling step ourselves.
    page.clock.install();page.select_option('#speed','25');page.locator('#ai').click();page.clock.run_for(55000)
    assert page.evaluate('snakeSnapshot().score')==15
    page.screenshot(path=str(ROOT/'assets/snake_ai_pass.png'),full_page=True)
    page.set_viewport_size({'width':390,'height':844});page.reload();assert page.evaluate('document.documentElement.scrollWidth')<=390
    page.screenshot(path=str(ROOT/'assets/snake_mobile.png'),full_page=True)
    page.on('dialog',lambda dialog:dialog.accept());page.locator('#reset').click();assert page.evaluate('snakeSnapshot().saved.games')==0
    page.goto((ROOT/'index.html').as_uri());page.set_viewport_size({'width':1100,'height':950});page.screenshot(path=str(ROOT/'assets/site_preview.png'),full_page=True)
    assert not errors,errors
    result.update({'interval_auto_demo':'pass','theme_reload':'pass','history_last_10':'pass','reset':'pass','mobile_overflow':'none','javascript_errors':errors,'environment':'headless Chromium / file://; accelerated virtual clock plus actual step logic'})
    (ROOT/'tests/game_acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k!='records'},ensure_ascii=False,indent=2))
    browser.close()
