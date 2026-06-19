import {
  useRef,
  useState,
  type JSX,
  type KeyboardEvent as ReactKeyboardEvent,
  type PointerEvent as ReactPointerEvent,
} from "react";

import { SEG_DEG } from "../constants";
import type { Chromatic, Role } from "../types";
import { CyclopsEye } from "./CyclopsEye";
import { InnerDisc } from "./InnerDisc";
import { OuterDisc } from "./OuterDisc";

interface WheelProps {
  readonly roles: readonly Role[];
  readonly chromatic: Chromatic;
  readonly tonicOffset: number;
  readonly onSetTonic: (note: string) => void;
  readonly onStep: (delta: number) => void;
}

interface DragState {
  readonly startAngle: number;
  readonly startOffset: number;
  readonly pointerId: number;
  // Cached at pointerdown to avoid forcing layout on every move.
  readonly centerX: number;
  readonly centerY: number;
}

function chromaticAt(chromatic: Chromatic, idx: number): string {
  // Modulo math elsewhere in the app guarantees idx is in 0..11; keep the
  // safety net anyway so a future refactor can't silently produce undefined.
  const note = chromatic[((idx % 12) + 12) % 12];
  if (note === undefined) {
    throw new Error(`chromatic index out of range: ${idx}`);
  }
  return note;
}

export function Wheel({
  roles,
  chromatic,
  tonicOffset,
  onSetTonic,
  onStep,
}: WheelProps): JSX.Element {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [drag, setDrag] = useState<DragState | null>(null);
  // Single source: visual rotation = baseRotation + transient drag delta.
  // No separate dragRotation state — eliminates the snap-back flash window
  // between endDrag (clears drag) and the parent re-render with new tonicOffset.
  const [dragDelta, setDragDelta] = useState<number>(0);

  const baseRotation = -tonicOffset * SEG_DEG;
  const rotation = drag !== null ? -drag.startOffset * SEG_DEG + dragDelta : baseRotation;

  function pointerAngleFromCenter(
    event: ReactPointerEvent<SVGSVGElement>,
    cx: number,
    cy: number,
  ): number {
    return Math.atan2(event.clientY - cy, event.clientX - cx) * (180 / Math.PI);
  }

  function handlePointerDown(event: ReactPointerEvent<SVGSVGElement>): void {
    const target = event.target as Element | null;
    if (target?.closest(".note-item")) return;
    const svg = svgRef.current;
    if (!svg) return;
    const rect = svg.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    setDrag({
      startAngle: pointerAngleFromCenter(event, centerX, centerY),
      startOffset: tonicOffset,
      pointerId: event.pointerId,
      centerX,
      centerY,
    });
    setDragDelta(0);
    svg.setPointerCapture(event.pointerId);
  }

  function handlePointerMove(event: ReactPointerEvent<SVGSVGElement>): void {
    if (!drag) return;
    const angle = pointerAngleFromCenter(event, drag.centerX, drag.centerY);
    setDragDelta(angle - drag.startAngle);
  }

  function endDrag(event: ReactPointerEvent<SVGSVGElement>): void {
    if (!drag) return;
    const angle = pointerAngleFromCenter(event, drag.centerX, drag.centerY);
    const delta = angle - drag.startAngle;
    const semitones = Math.round(delta / SEG_DEG);
    const newOffset = ((drag.startOffset + semitones) % 12 + 12) % 12;
    svgRef.current?.releasePointerCapture(drag.pointerId);
    setDrag(null);
    setDragDelta(0);
    onSetTonic(chromaticAt(chromatic, newOffset));
  }

  function handleKeyDown(event: ReactKeyboardEvent<SVGSVGElement>): void {
    if (event.key === "ArrowLeft") {
      event.preventDefault();
      onStep(-1);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      onStep(1);
    } else if (event.key === "Home") {
      event.preventDefault();
      onSetTonic("A");
    }
  }

  const dragging = drag !== null;

  return (
    <svg
      id="wheel"
      ref={svgRef}
      viewBox="-260 -260 520 520"
      role="slider"
      tabIndex={0}
      aria-label="Rueda de tónica del Gátople"
      aria-valuemin={0}
      aria-valuemax={11}
      aria-valuenow={tonicOffset}
      aria-valuetext={chromaticAt(chromatic, tonicOffset)}
      className={dragging ? "dragging" : undefined}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={endDrag}
      onPointerCancel={endDrag}
      onKeyDown={handleKeyDown}
    >
      <OuterDisc roles={roles} />
      <InnerDisc
        roles={roles}
        rotationDeg={rotation}
        dragging={dragging}
        onNoteClick={onSetTonic}
      />
      <CyclopsEye />
    </svg>
  );
}
