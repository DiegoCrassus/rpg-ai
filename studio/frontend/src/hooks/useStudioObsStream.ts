import { useEffect, useRef, useState } from "react";

import { matchesObsFilters, studioObsEventsUrl } from "../api/obsQuery";
import type { ObsFilterParams, ObsStreamStatus, StudioEvent } from "../types/observability";

type UseStudioObsStreamOptions = {
  enabled?: boolean;
  filters?: ObsFilterParams;
  since?: string | null;
  onEvent: (event: StudioEvent) => void;
};

export function useStudioObsStream({
  enabled = true,
  filters = {},
  since = null,
  onEvent,
}: UseStudioObsStreamOptions): ObsStreamStatus {
  const [status, setStatus] = useState<ObsStreamStatus>("idle");
  const onEventRef = useRef(onEvent);
  onEventRef.current = onEvent;

  useEffect(() => {
    if (!enabled || typeof EventSource === "undefined") {
      setStatus("idle");
      return;
    }

    const url = studioObsEventsUrl({
      since: since ?? undefined,
      limit: filters.limit ?? 100,
    });
    setStatus("connecting");
    const source = new EventSource(url);

    const handleObs = (message: MessageEvent<string>) => {
      try {
        const event = JSON.parse(message.data) as StudioEvent;
        if (!matchesObsFilters(event, filters)) {
          return;
        }
        onEventRef.current(event);
      } catch {
        /* ignore malformed SSE payloads */
      }
    };

    source.addEventListener("studio.obs", handleObs as EventListener);
    source.onopen = () => setStatus("open");
    source.onerror = () => setStatus("error");

    return () => {
      source.removeEventListener("studio.obs", handleObs as EventListener);
      source.close();
      setStatus("closed");
    };
  }, [
    enabled,
    since,
    filters.category,
    filters.card,
    filters.run_id,
    filters.event_type,
    filters.limit,
  ]);

  return status;
}
