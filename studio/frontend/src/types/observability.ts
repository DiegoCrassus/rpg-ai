export type EventCategory = "gateway" | "obs" | "handoff" | "gate";

export type EventCorrelation = {
  run_id?: string | null;
  card?: string | null;
  branch?: string | null;
  session_id?: string | null;
};

export type StudioEvent = {
  schema_version: string;
  event_id: string;
  event_type: string;
  category: EventCategory;
  timestamp: string;
  source: string;
  correlation_id: string;
  correlation: EventCorrelation;
  payload: Record<string, unknown>;
};

export type TimelineResponse = {
  events: StudioEvent[];
  count: number;
};

export type ObsFilterParams = {
  category?: EventCategory;
  card?: string;
  run_id?: string;
  event_type?: string;
  limit?: number;
};

export type ObsStreamStatus = "idle" | "connecting" | "open" | "error" | "closed";
