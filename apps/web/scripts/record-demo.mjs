// Reproducible silent, captioned screen capture of the synthetic local preview.
// Run only against the local FastAPI app; never against a live marketplace.
import { chromium } from '@playwright/test'
import { mkdir } from 'node:fs/promises'

const output = '../../tmp/demo-video'
await mkdir(output, { recursive: true })
const browser = await chromium.launch({ headless: true, channel: 'chrome' })
const context = await browser.newContext({ viewport: { width: 1280, height: 720 }, recordVideo: { dir: output, size: { width: 1280, height: 720 } } })
const page = await context.newPage()

async function caption(text, hold = 13000) {
  await page.evaluate(value => {
    let box = document.getElementById('demo-caption')
    if (!box) {
      box = document.createElement('div')
      box.id = 'demo-caption'
      Object.assign(box.style, {
        position: 'fixed', bottom: '16px', left: '300px', right: '24px', zIndex: '99999',
        padding: '13px 19px', background: 'rgba(15,32,52,.94)', color: 'white',
        fontFamily: 'Arial,sans-serif', fontSize: '20px', lineHeight: '1.3', borderRadius: '10px',
        boxShadow: '0 8px 30px rgba(0,0,0,.23)', pointerEvents: 'none',
      })
      document.body.appendChild(box)
    }
    box.textContent = value
  }, text)
  await page.waitForTimeout(hold)
}

try {
  await page.goto('http://127.0.0.1:8020/')
  await page.getByRole('heading', { name: 'Job inbox' }).waitFor()
  await caption('GigBid synthetic preview: each proposal needs evidence and explicit human approval.')

  await page.locator('.job-card').first().click()
  await page.getByRole('button', { name: 'Approve draft' }).waitFor()
  await caption('The bid graph analyses requirements, risk and portfolio fit in parallel.')
  await page.locator('.detail').evaluate(element => element.scrollIntoView({ behavior: 'instant' }))
  await caption('The decision desk shows the recommendation, risk signals and supporting portfolio items.')
  await page.getByRole('heading', { name: 'Proposal studio' }).evaluate(element => element.scrollIntoView({ behavior: 'instant' }))
  await caption('A bounded Critic loop revises a generic opening. The draft cites synthetic evidence.')
  await caption('The marketplace receives no draft while this LangGraph run waits for review.')
  await page.getByRole('button', { name: 'Approve draft' }).click()
  await page.getByText(/Approved draft created:/).waitFor()
  await caption('After approval, the development marketplace records one synthetic draft.')

  await page.getByRole('heading', { name: 'Client messages' }).evaluate(element => element.scrollIntoView({ behavior: 'instant' }))
  await caption('A synthetic client asks for an interview; the Workspace MCP mock supplies free slots.')
  await page.getByRole('button', { name: 'Prepare reply for selected job' }).click()
  await page.getByRole('button', { name: 'Approve message' }).waitFor()
  await caption('The Client Liaison drafts a reply and pauses at a second human approval gate.')
  await page.getByRole('button', { name: 'Approve message' }).click()
  await page.getByText(/Approved synthetic message recorded:/).waitFor()
  await caption('The approved reply is recorded as a synthetic message. No real client is contacted.')

  await page.locator('.job-card').nth(1).evaluate(element => element.scrollIntoView({ behavior: 'instant' }))
  await page.locator('.job-card').nth(1).click()
  await page.getByText('SKIP', { exact: true }).waitFor()
  await caption('Scam example: a free-work and off-platform contact request is skipped before drafting.')
  await page.locator('.job-card').nth(2).click()
  await page.getByText('Job post contains an instruction aimed at the assistant').waitFor()
  await caption('Prompt-injection example: the agent refuses the instruction to claim false experience.')

  await page.getByRole('heading', { name: 'Demo setup' }).evaluate(element => element.scrollIntoView({ behavior: 'instant' }))
  await caption('Scope: this is a synthetic development preview. The example kit has no working GigSim or evaluation labels.')
  console.log(await page.video().path())
} finally {
  await context.close()
  await browser.close()
}
