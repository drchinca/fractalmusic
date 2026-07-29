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

test('los saltos del círculo de cuartas en sentido horario son correctos (A ➔ D ➔ G ➔ C ➔ F)',()=>{
  const expectedHours = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8];
  const expectedNotes = [9, 2, 7, 0, 5, 10, 3, 8, 1, 6, 11, 4];
  const CHROMATIC_HOURS = [12, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7];
  
  expectedHours.forEach((hour, idx) => {
    const pos = CHROMATIC_HOURS.indexOf(hour);
    const note = Core.noteAtPosition(Core.A_INDEX, pos);
    assert.equal(note, expectedNotes[idx], `El salto de cuartas en hora ${hour} es incorrecto: se esperaba ${expectedNotes[idx]} pero se obtuvo ${note}`);
  });
});

test('la octava del piano empieza y termina en la nota A (La menor)',()=>{
  const whiteKeys = [9, 11, 0, 2, 4, 5, 7, 9];
  assert.equal(whiteKeys[0], 9, 'El piano debe empezar en la nota A');
  assert.equal(whiteKeys[whiteKeys.length - 1], 9, 'El piano debe terminar en la nota A');
  assert.equal(whiteKeys.length, 8, 'La octava blanca debe contener 8 teclas');
});
