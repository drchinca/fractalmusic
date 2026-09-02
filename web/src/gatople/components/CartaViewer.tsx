import { type JSX, useState } from "react";

import type { Role } from "../types";

interface CartaViewerProps {
  readonly roles: readonly Role[];
  readonly tonicNote: string;
  readonly displayTonicNote: string;
}

export function CartaViewer({ roles, tonicNote, displayTonicNote }: CartaViewerProps): JSX.Element | null {
  const [imageFailed, setImageFailed] = useState(false);
  // Each of the 12 painted cartas is fixed to its role (Cardinal Invariant #5)
  // and never moves with the wheel — the role currently sitting at the tonic
  // slot is always Eólico, so "which carta is at the tonic" is degenerate.
  // What actually answers "show me the tonic's carta" is: which of the 12
  // cards has this note as its own home identity (note_default).
  const homeRole = roles.find((r) => r.note_default === tonicNote);
  if (homeRole === undefined) return null;

  return (
    <div className="carta-viewer">
      <h2>Carta de la tónica</h2>
      {imageFailed ? (
        <p className="carta-viewer-fallback">
          {homeRole.carta_name} — {homeRole.mode_name}
        </p>
      ) : (
        <img
          className="carta-viewer-image"
          src={`/${homeRole.carta_image}`}
          alt={`Carta ${homeRole.carta_name} (${homeRole.mode_name}), tónica ${displayTonicNote}`}
          onError={() => setImageFailed(true)}
        />
      )}
      <p className="carta-viewer-caption">
        {homeRole.carta_name} · tónica {displayTonicNote} · {homeRole.mode_name}
      </p>
    </div>
  );
}
