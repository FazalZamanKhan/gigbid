import { expect, test } from '@playwright/test'

async function analyseFirstJob(page: import('@playwright/test').Page) {
  await page.goto('/')
  await page.locator('.job-card').first().click()
  await expect(page.getByRole('button', { name: 'Approve draft' })).toBeVisible()
}

test('synthetic onboarding saves the reviewer profile locally', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('link', { name: /Demo setup/ }).click()
  await page.getByLabel('Display name').fill('Synthetic reviewer')
  await page.getByLabel('Hourly rate (USD)').fill('45')
  await page.getByLabel('Weekly Connects budget').fill('32')
  await page.getByRole('button', { name: 'Save demo profile' }).click()
  await expect(page.getByRole('status')).toHaveText('Demo profile saved on this browser.')
  await page.reload()
  await expect(page.getByLabel('Display name')).toHaveValue('Synthetic reviewer')
  await expect(page.getByLabel('Hourly rate (USD)')).toHaveValue('45')
  await expect(page.getByLabel('Weekly Connects budget')).toHaveValue('32')
})

test('reviewer approves a cited proposal', async ({ page }) => {
  await analyseFirstJob(page)
  await page.getByRole('button', { name: 'Approve draft' }).click()
  await expect(page.getByText(/Approved draft created:/)).toBeVisible()
})

test('reviewer rejects a proposal with a reason', async ({ page }) => {
  await analyseFirstJob(page)
  await page.getByLabel('Reason if rejecting').fill('Budget is below my minimum')
  await page.getByRole('button', { name: 'Reject', exact: true }).click()
  await expect(page.getByText('Budget is below my minimum')).toBeVisible()
  await expect(page.getByText(/Approved draft created:/)).toHaveCount(0)
})

test('edited proposal is held for claim and compliance review', async ({ page }) => {
  await analyseFirstJob(page)
  await page.getByLabel('Draft', { exact: true }).fill('I have built this exact client product before.')
  await page.getByRole('button', { name: 'Approve draft' }).click()
  await expect(page.getByText(/Edited draft needs claim and compliance recheck/)).toBeVisible()
})

test('marketplace outage shows a degraded mode banner', async ({ page }) => {
  await page.route('**/api/jobs', route => route.fulfill({ status: 503, contentType: 'application/json', body: JSON.stringify({ detail: 'Marketplace MCP is down' }) }))
  await page.goto('/')
  await expect(page.getByRole('alert')).toContainText('Marketplace unavailable')
})

test('scam and injected job are skipped before approval', async ({ page }) => {
  await page.goto('/')
  await page.locator('.job-card').nth(1).click()
  await expect(page.getByText('SKIP', { exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Approve draft' })).toHaveCount(0)
  await page.locator('.job-card').nth(2).click()
  await expect(page.getByText('Job post contains an instruction aimed at the assistant')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Approve draft' })).toHaveCount(0)
})

test('client reply waits for approval and then records a synthetic message', async ({ page }) => {
  await analyseFirstJob(page)
  await page.getByRole('button', { name: 'Prepare reply for selected job' }).click()
  await expect(page.getByRole('button', { name: 'Approve message' })).toBeVisible()
  await page.getByRole('button', { name: 'Approve message' }).click()
  await expect(page.getByText(/Approved synthetic message recorded:/)).toBeVisible()
})
