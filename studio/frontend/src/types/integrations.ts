export type PlaneCardState = {
  id?: string;
  name: string;
  group?: string;
};

export type PlaneCardDetail = {
  card: string;
  name: string;
  state: PlaneCardState;
  priority?: string;
  description_present: boolean;
  plane_url: string;
  parent?: string | null;
};

export type PlaneWorkFeedItem = {
  card: string;
  name: string;
  state: PlaneCardState;
  priority?: string;
  updated_at?: string;
  plane_url: string;
};

export type PlaneWorkFeedResponse = {
  items: PlaneWorkFeedItem[];
  count: number;
  fetched_at?: string;
};

export type PlaneEpicChild = {
  card: string;
  name: string;
  state: PlaneCardState;
};

export type PlaneEpicChildrenResponse = {
  epic: string;
  total: number;
  children_by_state: Record<string, PlaneEpicChild[]>;
  fetched_at?: string;
};

export type GitHubPullHead = {
  ref: string;
  sha?: string;
};

export type GitHubPull = {
  number: number;
  title: string;
  state: string;
  draft: boolean;
  head: GitHubPullHead;
  base: GitHubPullHead;
  html_url: string;
  user?: string;
  created_at?: string;
  updated_at?: string;
};

export type GitHubPullsResponse = {
  repository: string;
  owner: string;
  base: string;
  pulls: GitHubPull[];
  count: number;
  fetched_at?: string;
};

export type GitHubCommitStatus = {
  sha: string;
  message?: string;
  combined_status?: string;
  statuses?: { context: string; state: string }[];
};

export type GitHubWorkflowRun = {
  id: number;
  name: string;
  status: string;
  conclusion?: string | null;
  event?: string;
  html_url: string;
  created_at?: string;
  updated_at?: string;
};

export type GitHubChecksResponse = {
  repository: string;
  ref: string;
  commit: GitHubCommitStatus;
  workflow_runs: GitHubWorkflowRun[];
  fetched_at?: string;
};
