(() => {
  'use strict';
  const Core=window.GatopleCore;
  if(!Core) throw new Error('GatopleCore no fue cargado.');

  const NOTES=['C','C♯','D','D♯','E','F','F♯','G','G♯','A','A♯','B'];
  const ROLES=['Centro','Umbral','Impulso','Fricción','Color','Puente','Abismo','Dirección','Espejo','Memoria','Expansión','Retorno'];
  const GLYPHS=['●','◐','△','✕','◇','⌁','⬡','→','◈','∞','✦','↺'];
  const COLORS=['#e4aa24','#12b75a','#1d5ee7','#842fc1','#d51c2e','#e06c22','#d8c94a','#38a7a0','#5a79df','#af4db6','#e45a7d','#c79335'];
  const state={tonic:Core.A_INDEX,octave:4,dragging:false,startAngle:0,startTonic:Core.A_INDEX,moved:false,pointerId:null};
  const $=id=>document.getElementById(id);
  const svg=$('wheelSvg'),noteRing=$('noteRing'),fixedRing=$('fixedRing');
  let audioCtx=null;

  function polar(cx,cy,r,a){const rad=(a-90)*Math.PI/180;return{x:cx+r*Math.cos(rad),y:cy+r*Math.sin(rad)}}
  function wedgePath(i,outer=230,inner=135){const a0=i*30,a1=a0+30;const p1=polar(300,300,outer,a0),p2=polar(300,300,outer,a1),q2=polar(300,300,inner,a1),q1=polar(300,300,inner,a0);return `M ${p1.x} ${p1.y} A ${outer} ${outer} 0 0 1 ${p2.x} ${p2.y} L ${q2.x} ${q2.y} A ${inner} ${inner} 0 0 0 ${q1.x} ${q1.y} Z`}
  function polygonPoints(indices,r){return indices.map(i=>{const p=polar(300,300,r,i*30);return `${p.x},${p.y}`}).join(' ')}

  function buildWheel(){
    noteRing.innerHTML='';fixedRing.innerHTML='';
    for(let pos=0;pos<12;pos++){
      const fixed=document.createElementNS('http://www.w3.org/2000/svg','g');
      const sector=document.createElementNS(fixed.namespaceURI,'path');sector.setAttribute('d',wedgePath(pos,255,232));sector.setAttribute('class','fixed-sector');sector.style.fill=COLORS[pos];
      const gp=polar(300,300,244,pos*30+15);const glyph=document.createElementNS(fixed.namespaceURI,'text');glyph.setAttribute('x',gp.x);glyph.setAttribute('y',gp.y);glyph.setAttribute('class','fixed-glyph');glyph.textContent=GLYPHS[pos];
      fixed.append(sector,glyph);fixedRing.appendChild(fixed);

      const g=document.createElementNS('http://www.w3.org/2000/svg','g');
      const path=document.createElementNS(g.namespaceURI,'path');path.setAttribute('d',wedgePath(pos));path.setAttribute('class','segment');path.dataset.position=pos;
      const np=polar(300,300,183,pos*30+15);const text=document.createElementNS(g.namespaceURI,'text');text.setAttribute('x',np.x);text.setAttribute('y',np.y);text.setAttribute('class','segment-label');text.dataset.position=pos;
      g.append(path,text);noteRing.appendChild(g);
      path.addEventListener('pointerenter',()=>showRole(pos));
      path.addEventListener('click',()=>{if(state.moved)return;const note=Core.noteAtPosition(state.tonic,pos);playNote(note,state.octave+(pos===0?0:0));setTonic(note);showRole(Core.ORIGIN_POSITION)});
    }
    $('heptagon').setAttribute('points',polygonPoints([0,2,4,5,7,9,11],108));
    $('pentagram').setAttribute('points',polygonPoints([0,5,10,3,8,0],92));
  }

  function update(){
    [...noteRing.children].forEach((g,pos)=>{
      const note=Core.noteAtPosition(state.tonic,pos),path=g.querySelector('path'),text=g.querySelector('text');
      path.style.fill=COLORS[pos];path.style.opacity=pos===Core.ORIGIN_POSITION?'1':'.78';path.classList.toggle('active',pos===Core.ORIGIN_POSITION);text.textContent=NOTES[note];
    });
    $('tonicLabel').textContent=NOTES[state.tonic];$('modeLabel').textContent=Core.MODALITY;$('octaveLabel').textContent=`Octava ${state.octave}`;
    renderTable();renderPiano();renderFretboard();showRole(Core.ORIGIN_POSITION);
  }

  function showRole(position){
    const note=Core.noteAtPosition(state.tonic,position);
    $('activeRole').textContent=`${ROLES[position]} · ${NOTES[note]}`;
    $('activeDescription').textContent=`Posición ${Core.hourForPosition(position)} h · función fija ${position+1}/12. La nota cambia al girar; el glifo permanece en su estación.`;
    $('roleSwatch').style.background=COLORS[position];
  }
  function setTonic(index){state.tonic=Core.mod(index);update()}
  function renderTable(){const body=$('linksTable');body.innerHTML='';for(let pos=0;pos<12;pos++){const note=Core.noteAtPosition(state.tonic,pos),tr=document.createElement('tr');tr.innerHTML=`<td>${ROLES[pos]}</td><td>${GLYPHS[pos]}</td><td>${NOTES[note]}</td><td>${Core.hourForPosition(pos)}</td>`;body.appendChild(tr)}}
  function midi(note,oct){return (oct+1)*12+note}
  function playNote(note,oct=4,duration=.75){audioCtx ||= new (window.AudioContext||window.webkitAudioContext)();if(audioCtx.state==='suspended')audioCtx.resume();const now=audioCtx.currentTime,osc=audioCtx.createOscillator(),gain=audioCtx.createGain();osc.type='sine';osc.frequency.value=440*Math.pow(2,(midi(note,oct)-69)/12);gain.gain.setValueAtTime(.0001,now);gain.gain.exponentialRampToValueAtTime(.22,now+.02);gain.gain.exponentialRampToValueAtTime(.0001,now+duration);osc.connect(gain).connect(audioCtx.destination);osc.start(now);osc.stop(now+duration+.02)}
  function renderPiano(){const piano=$('piano');piano.innerHTML='';const white=[0,2,4,5,7,9,11,0],black=[1,3,null,6,8,10,null];white.forEach((n,i)=>{const actual=n,octaveOffset=i===7?1:0,pos=Core.positionForNote(state.tonic,actual),b=document.createElement('button');b.type='button';b.className='key white';b.dataset.note=actual;b.dataset.octaveOffset=octaveOffset;b.innerHTML=`<span class="key-label"><span class="key-role" style="color:${COLORS[pos]}">${GLYPHS[pos]}</span>${NOTES[actual]}${octaveOffset?'<sup>+1</sup>':''}</span>`;b.addEventListener('click',e=>triggerKey(e.currentTarget,actual,false,octaveOffset));piano.appendChild(b)});black.forEach((n,i)=>{if(n==null)return;const pos=Core.positionForNote(state.tonic,n),b=document.createElement('button');b.type='button';b.className='key black';b.style.left=`${(i+1)*12.5}%`;b.dataset.note=n;b.dataset.octaveOffset=0;b.innerHTML=`<span class="key-label"><span class="key-role" style="color:${COLORS[pos]}">${GLYPHS[pos]}</span>${NOTES[n]}</span>`;b.addEventListener('click',e=>triggerKey(e.currentTarget,n,false,0));piano.appendChild(b)})}
  function triggerKey(el,note,shift,octaveOffset=0){playNote(note,state.octave+octaveOffset);if(el){el.classList.add('active');setTimeout(()=>el.classList.remove('active'),160)}if(shift)setTonic(note)}
  function renderFretboard(){const board=$('fretboard');board.innerHTML='';const tuning=[4,11,7,2,9,4];['E','B','G','D','A','E'].forEach((name,row)=>{const label=document.createElement('div');label.className='fret string-name';label.textContent=name;board.appendChild(label);for(let f=0;f<=12;f++){const note=(tuning[row]+f)%12,pos=Core.positionForNote(state.tonic,note),cell=document.createElement('button');cell.type='button';cell.className='fret';cell.title=`${name}${f}: ${NOTES[note]} · ${ROLES[pos]}`;cell.innerHTML=`<span class="note-dot" style="background:${COLORS[pos]}; display: flex; flex-direction: column; align-items: center; justify-content: center; line-height: 1.1; font-size: 10px; padding: 2px 0;"><span style="font-weight: 800; font-size: 11px; display: block; margin-bottom: -1px;">${GLYPHS[pos]}</span><span style="font-size: 8px; font-weight: 500; display: block; opacity: 0.95;">${NOTES[note]}</span></span>`;cell.addEventListener('click',()=>playNote(note,state.octave+(row===0?1:0)));board.appendChild(cell)}})}
  function angleFromEvent(e){const r=svg.getBoundingClientRect(),x=e.clientX-(r.left+r.width/2),y=e.clientY-(r.top+r.height/2);return Math.atan2(y,x)*180/Math.PI}
  svg.addEventListener('pointerdown',e=>{state.dragging=true;state.moved=false;state.pointerId=e.pointerId;state.startAngle=angleFromEvent(e);state.startTonic=state.tonic;svg.setPointerCapture(e.pointerId)});
  svg.addEventListener('pointermove',e=>{if(!state.dragging||e.pointerId!==state.pointerId)return;const steps=Core.semitoneStepsFromDrag(state.startAngle,angleFromEvent(e));if(Math.abs(steps)>0)state.moved=true;const next=Core.mod(state.startTonic+steps);if(next!==state.tonic)setTonic(next)});
  function endDrag(e){if(e&&state.pointerId!==null&&e.pointerId!==state.pointerId)return;state.dragging=false;state.pointerId=null;setTimeout(()=>{state.moved=false},0)}
  svg.addEventListener('pointerup',endDrag);svg.addEventListener('pointercancel',endDrag);svg.addEventListener('lostpointercapture',endDrag);

  $('prevButton').addEventListener('click',()=>setTonic(state.tonic-1));$('nextButton').addEventListener('click',()=>setTonic(state.tonic+1));$('resetButton').addEventListener('click',()=>setTonic(Core.A_INDEX));
  $('hMinusButton').addEventListener('click',()=>setTonic(Core.rotateHMinus(state.tonic)));$('hPlusButton').addEventListener('click',()=>setTonic(Core.rotateHPlus(state.tonic)));
  $('zeroButton').addEventListener('click',()=>Core.zeroPythagoras(state.tonic).forEach((n,i)=>setTimeout(()=>playNote(n,3+(i>1?1:0),.9),i*280)));
  $('polygonToggle').addEventListener('change',e=>$('heptagon').classList.toggle('hidden',!e.target.checked));$('starToggle').addEventListener('change',e=>$('pentagram').classList.toggle('hidden',!e.target.checked));$('zonesToggle').addEventListener('change',e=>$('zoneGuides').classList.toggle('hidden',!e.target.checked));
  const keyMap={a:{note:0,off:0},w:{note:1,off:0},s:{note:2,off:0},e:{note:3,off:0},d:{note:4,off:0},f:{note:5,off:0},t:{note:6,off:0},g:{note:7,off:0},y:{note:8,off:0},h:{note:9,off:0},u:{note:10,off:0},j:{note:11,off:0},k:{note:0,off:1}};
  document.addEventListener('keydown',e=>{
    if(e.repeat)return;
    const key=e.key;
    if(key==='ArrowLeft'){e.preventDefault();setTonic(state.tonic-1);return}
    if(key==='ArrowRight'){e.preventDefault();setTonic(state.tonic+1);return}
    const lKey=key.toLowerCase();
    if(lKey==='z'){state.octave=Math.max(1,state.octave-1);update();return}
    if(lKey==='x'){state.octave=Math.min(7,state.octave+1);update();return}
    const mapped=keyMap[lKey];
    if(!mapped)return;
    e.preventDefault();
    const candidates=[...$('piano').querySelectorAll(`[data-note="${mapped.note}"]`)];
    const el=candidates.find(node=>Number(node.dataset.octaveOffset)===mapped.off)||candidates[0];
    triggerKey(el,mapped.note,e.shiftKey,mapped.off);
  });
  buildWheel();update();
})();
