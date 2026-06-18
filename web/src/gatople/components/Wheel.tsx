import { useRef, useState, type PointerEvent as ReactPointerEvent } from "react";

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
}

interface DragState {
  readonly startAngle: number;
  readonly startOffset: number;
  readonly pointerId: number;
}

export function Wheel({
  roles,
  chromatic,
  tonicOffset,
  onSetTonic,
}: WheelProps): JSX.Element {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [drag, setDrag] = useState<DragState | null>(null);
  const [dragRotation, setDragRotation] = useState<number | null>(null);

  const baseRotation = -tonicOffset * SEG_DEG;
  const rotation = dragRotation ?? baseRotation;

  function pointerAngle(event: ReactPointerEvent<SVGSVGElement>): number {
    const svg = svgRef.current;
    if (!svg) return 0;
    const rect = svg.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    return Math.atan2(event.clientY - cy, event.clientX - cx) * (180 / Math.PI);
  }

  function handlePointerDown(event: ReactPointerEvent<SVGSVGElement>): void {
    const target = event.target as Element | null;
    if (target?.closest(".note-item")) return;
    const startAngle = pointerAngle(event);
    setDrag({ startAngle, startOffset: tonicOffset, pointerId: event.pointerId });
    setDragRotation(baseRotation);
    svgRef.current?.setPointerCapture(event.pointerId);
  }

  function handlePointerMove(event: ReactPointerEvent<SVGSVGElement>): void {
    if (!drag) return;
    const delta = pointerAngle(event) - drag.startAngle;
    setDragRotation(-drag.startOffset * SEG_DEG + delta);
  }

  function endDrag(event: ReactPointerEvent<SVGSVGElement>): void {
    if (!drag) return;
    const delta = pointerAngle(event) - drag.startAngle;
    const semitones = Math.round(delta / SEG_DEG);
    const newOffset = ((drag.startOffset + semitones) % 12 + 12) % 12;
    svgRef.current?.releasePointerCapture(drag.pointerId);
    setDrag(null);
    setDragRotation(null);
    onSetTonic(chromatic[newOffset]);
  }

  const dragging = drag !== null;

  return (
    <svg
      id="wheel"
      ref={svgRef}
      viewBox="-260 -260 520 520"
      aria-label="Gátople wheel"
      className={dragging ? "dragging" : undefined}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={endDrag}
      onPointerCancel={endDrag}
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
