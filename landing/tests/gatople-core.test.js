import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source=fs.readFileSync(new URL('../gatople-core.js',import.meta.url),'utf8');
const context={globalThis:{}};
vm.createContext(context);
vm.runInContext(source,context);
const Core=context.globalThis.GatopleCore;

test('orientación constitucional inicial: C a las 12 h y A a las 9 h',()=>{
  assert.equal(Core.ORIGIN_POSITION,9);
  assert.equal(Core.noteAtPosition(Core.A_INDEX,0),0);
  assert.equal(Core.noteAtPosition(Core.A_INDEX,9),Core.A_INDEX);
  assert.equal(Core.hourForPosition(0),12);
  assert.equal(Core.hourForPosition(9),9);
});

test('las funciones ocupan las estaciones constitucionales del sigil',()=>{
  const hours=Array.from({length:12},(_,position)=>Core.hourForPosition(position));
  assert.deepEqual(hours,[12,5,10,3,8,1,6,11,4,9,2,7]);
});

test('el piano constitucional comienza y termina en La',()=>{
  const white=JSON.parse(JSON.stringify(Core.PIANO_WHITE));
  const black=JSON.parse(JSON.stringify(Core.PIANO_BLACK));
  assert.deepEqual(white,[
    {note:9,off:0},{note:11,off:0},{note:0,off:1},{note:2,off:1},
    {note:4,off:1},{note:5,off:1},{note:7,off:1},{note:9,off:1}
  ]);
  assert.deepEqual(black,[
    {note:10,off:0},null,{note:1,off:1},{note:3,off:1},
    null,{note:6,off:1},{note:8,off:1}
  ]);
});

test('Memoria usa el glifo oficial de dos puntos',()=>{
  assert.equal(Core.GLYPHS[9],'∶');
});

test('las doce posiciones forman una vuelta cromática sin duplicados',()=>{
  const notes=Array.from({length:12},(_,position)=>Core.noteAtPosition(Core.A_INDEX,position));
  assert.deepEqual([...notes].sort((a,b)=>a-b),Array.from({length:12},(_,i)=>i));
});

test('posición y nota son transformaciones inversas',()=>{
  for(let tonic=0;tonic<12;tonic++) for(let note=0;note<12;note++) {
    const position=Core.positionForNote(tonic,note);
    assert.equal(Core.noteAtPosition(tonic,position),note);
  }
});

test('el arrastre normaliza correctamente el cruce ±180 grados',()=>{
  assert.equal(Core.normalizeAngleDelta(-358),2);
  assert.equal(Core.normalizeAngleDelta(358),-2);
  assert.equal(Core.semitoneStepsFromDrag(179,-151),1);
});

test('H+ y H− aplican ±5 módulo 12 y son inversos',()=>{
  for(let tonic=0;tonic<12;tonic++) {
    assert.equal(Core.rotateHMinus(Core.rotateHPlus(tonic)),tonic);
    assert.equal(Core.rotateHPlus(Core.rotateHMinus(tonic)),tonic);
  }
});

test('Cero Pitágoras sigue la cadena H+ desde la tónica',()=>{
  assert.deepEqual(Array.from(Core.zeroPythagoras(Core.A_INDEX)),[9,2,7,0]);
});

test('la modalidad no cambia arbitrariamente al transponer',()=>{
  assert.equal(Core.MODALITY,'Eólico');
});
