import { expect, test, type Page } from "@playwright/test";

async function gotoBuilder(page: Page) {
  await page.goto("/builder");
  await expect(page.getByRole("heading", { name: "Workflow Builder", level: 1 })).toBeVisible({
    timeout: 15_000,
  });
  await expect(page.getByTestId("builder-shell")).toBeVisible({ timeout: 15_000 });
}

async function waitForCanvasReady(page: Page) {
  await expect(page.getByTestId("stage-node").first()).toBeVisible({ timeout: 15_000 });
}

async function countTransitionEdges(page: Page) {
  return page.getByTestId("transition-edge").count();
}

function stageNodeByLabel(page: Page, label: string) {
  return page.getByTestId("stage-node").filter({
    has: page.getByText(label, { exact: true }),
  });
}

async function prepareCanvasForConnect(page: Page) {
  const annotations = page.getByTestId("builder-show-annotations");
  if (await annotations.isChecked()) {
    await annotations.uncheck();
  }
  await page.getByRole("button", { name: "Fit View" }).click();
}

async function connectStagesByLabel(page: Page, sourceLabel: string, targetLabel: string) {
  const sourceHandle = stageNodeByLabel(page, sourceLabel).getByTestId("stage-handle-source");
  const targetHandle = stageNodeByLabel(page, targetLabel).getByTestId("stage-handle-target");
  await dragHandleToHandle(page, sourceHandle, targetHandle);
}

async function dragHandleToHandle(
  page: Page,
  sourceHandle: ReturnType<Page["getByTestId"]>,
  targetHandle: ReturnType<Page["getByTestId"]>,
) {
  await sourceHandle.scrollIntoViewIfNeeded();
  await targetHandle.scrollIntoViewIfNeeded();
  await sourceHandle.dragTo(targetHandle, { force: true });
}

async function deleteAllEdges(page: Page) {
  let stuckAt = -1;
  for (let attempt = 0; attempt < 30; attempt += 1) {
    const edges = page.getByTestId("transition-edge");
    const count = await edges.count();
    if (count === 0) {
      return;
    }
    if (count === stuckAt) {
      throw new Error(`Could not delete edges — stuck at ${count}`);
    }
    stuckAt = count;

    await edges.first().click({ force: true });
    await page.keyboard.press("Delete");
    await expect(edges).toHaveCount(count - 1, { timeout: 5_000 });
  }
  throw new Error("deleteAllEdges exceeded retry limit");
}

test.describe("Workflow Builder", () => {
  test.setTimeout(60_000);

  test.beforeEach(async ({ page }) => {
    await gotoBuilder(page);
    await waitForCanvasReady(page);
  });

  test("E2E-B1: /builder heading visible", async ({ page }) => {
    await expect(page.getByRole("heading", { name: "Workflow Builder", level: 1 })).toBeVisible();
    await expect(page.getByTestId("builder-page")).toBeVisible();
  });

  test("E2E-B2: canvas has ≥10 stage nodes or toolbox lists 10 stages", async ({ page }) => {
    const nodeCount = await page.getByTestId("stage-node").count();
    const toolboxCount = await page.getByTestId("builder-toolbox-stages").locator("li").count();
    expect(nodeCount >= 10 || toolboxCount >= 10).toBeTruthy();
  });

  test("E2E-B3: drag handle connection increases edge count", async ({ page }) => {
    const before = await countTransitionEdges(page);
    // Observability → Incident is not in the default lifecycle chain.
    await prepareCanvasForConnect(page);
    await connectStagesByLabel(page, "Observability", "Incident");
    await expect(page.getByTestId("transition-edge")).toHaveCount(before + 1, { timeout: 10_000 });
  });

  test("E2E-B4: inspector agent select after edge select", async ({ page }) => {
    await prepareCanvasForConnect(page);
    await connectStagesByLabel(page, "Observability", "Incident");
    await expect(page.getByTestId("builder-inspector-edge")).toBeVisible({ timeout: 10_000 });
    await expect(page.getByTestId("builder-inspector-agent")).toBeVisible();
    await expect(page.getByTestId("builder-inspector-agent")).toBeEnabled();
  });

  test("E2E-B5: create proposal disabled with 0 drafts, enabled with ≥1 edge", async ({
    page,
  }) => {
    const createButton = page.getByTestId("builder-create-proposal");

    await deleteAllEdges(page);
    await expect(createButton).toBeDisabled();
    await prepareCanvasForConnect(page);
    await connectStagesByLabel(page, "Observability", "Incident");
    await expect(page.getByTestId("transition-edge")).toHaveCount(1, { timeout: 10_000 });
    await expect(createButton).toBeEnabled();
  });

  test("E2E-B6: proposal panel unified diff non-empty after create", async ({ page }) => {
    await deleteAllEdges(page);
    await prepareCanvasForConnect(page);
    await connectStagesByLabel(page, "Observability", "Incident");
    await expect(page.getByTestId("transition-edge")).toHaveCount(1, { timeout: 10_000 });

    await page.getByTestId("builder-create-proposal").click();
    await expect(page.getByText("Proposal preview")).toBeVisible({ timeout: 15_000 });

    const diffPre = page.locator('p:text-is("Unified diff") + pre');
    await expect(diffPre).toBeVisible();
    const diffText = (await diffPre.textContent())?.trim() ?? "";
    expect(diffText.length).toBeGreaterThan(0);
    expect(diffText).not.toContain("(no diff — proposed content matches current file)");
    expect(diffText).toMatch(/^[+-@]/m);
  });
});
