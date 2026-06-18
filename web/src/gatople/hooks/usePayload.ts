import { useEffect, useState } from "react";

import type { Payload } from "../types";

interface PayloadState {
  readonly payload: Payload | null;
  readonly error: string | null;
}

export function usePayload(url: string): PayloadState {
  const [payload, setPayload] = useState<Payload | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch(url)
      .then((response): Promise<Payload> => {
        if (!response.ok) {
          throw new Error(`Failed to load ${url}: ${response.status}`);
        }
        return response.json() as Promise<Payload>;
      })
      .then((data) => {
        if (!cancelled) setPayload(data);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        const message = err instanceof Error ? err.message : String(err);
        setError(message);
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

  return { payload, error };
}
