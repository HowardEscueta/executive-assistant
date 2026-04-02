/**
 * BookMe Tutorial Recording
 * Records a step-by-step walkthrough of setting up a BookMe account.
 *
 * Usage:
 *   node record-demo.mjs
 *   node record-demo.mjs --url https://bookme-ochre.vercel.app
 *
 * Output: ./output/bookme-demo.webm
 * Convert to MP4: ffmpeg -i output/bookme-demo.webm output/bookme-demo.mp4
 */

import { chromium } from "playwright";
import { existsSync, mkdirSync, readdirSync, renameSync } from "fs";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUTPUT_DIR = join(__dirname, "output");
if (!existsSync(OUTPUT_DIR)) mkdirSync(OUTPUT_DIR, { recursive: true });

// Parse --url flag
const urlFlag = process.argv.indexOf("--url");
const BASE_URL = urlFlag !== -1 ? process.argv[urlFlag + 1] : "http://localhost:3001";

// Unique so re-runs don't conflict on the same database
const uid = Date.now().toString().slice(-5);
const slug = `juans-barbershop-${uid}`;
const email = `demo${uid}@example.com`;

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

async function slowType(locator, text, delay = 55) {
  await locator.click();
  await locator.pressSequentially(text, { delay });
}

async function smoothScroll(page, totalPx, steps = 20) {
  for (let i = 0; i < steps; i++) {
    await page.evaluate((d) => window.scrollBy(0, d), totalPx / steps);
    await wait(35);
  }
}

async function main() {
  console.log(`BASE URL : ${BASE_URL}`);
  console.log(`Output   : ${OUTPUT_DIR}/bookme-demo.webm\n`);

  const browser = await chromium.launch({ headless: false, slowMo: 15 });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: OUTPUT_DIR, size: { width: 1280, height: 720 } },
  });
  const page = await context.newPage();

  // ── 1. Homepage ────────────────────────────────────────────────────────────
  console.log("[1/8] Homepage");
  await page.goto(BASE_URL);
  await wait(2500);

  // Scroll through the landing page
  await smoothScroll(page, 350, 18);
  await wait(900);
  await smoothScroll(page, 400, 20);
  await wait(900);
  await smoothScroll(page, 500, 25);
  await wait(1200);

  // Scroll back to top
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: "smooth" }));
  await wait(1500);

  // ── 2. Sign Up ─────────────────────────────────────────────────────────────
  console.log("[2/8] Sign up");
  await page.getByRole("link", { name: "Get Started" }).first().click();
  await wait(1500);

  await slowType(page.getByLabel("Your name"), "Juan Dela Cruz");
  await wait(350);
  await slowType(page.getByLabel("Business name"), "Juan's Barbershop");
  await wait(350);
  await slowType(page.getByLabel("Your booking link"), slug);
  await wait(350);
  await slowType(page.getByLabel("Email"), email);
  await wait(350);
  await slowType(page.getByLabel("Password"), "password123");
  await wait(900);

  await page.getByRole("button", { name: "Create Account" }).click();
  // Wait for redirect to dashboard (up to 10s)
  try {
    await page.waitForURL("**/dashboard", { timeout: 10000 });
  } catch {
    // If redirect didn't happen, navigate manually
    await page.goto(`${BASE_URL}/dashboard`);
  }
  await wait(2000);

  // ── 3. Dashboard overview ──────────────────────────────────────────────────
  console.log("[3/8] Dashboard overview");
  await wait(1500);

  // ── 4. Add services ────────────────────────────────────────────────────────
  console.log("[4/8] Add services");
  await page.getByRole("button", { name: "services" }).click();
  await wait(800);

  // Service 1 – Haircut
  await page.getByRole("button", { name: "+ Add service" }).click();
  await wait(500);
  await slowType(page.getByPlaceholder("Service name"), "Haircut");
  await wait(250);
  const dur1 = page.getByPlaceholder("Duration (min)");
  await dur1.click({ clickCount: 3 });
  await dur1.pressSequentially("30", { delay: 55 });
  await wait(250);
  await slowType(page.getByPlaceholder("Price (PHP)"), "150");
  await wait(300);
  await page.getByRole("button", { name: "Add Service" }).click();
  await wait(1000);

  // Service 2 – Haircut + Beard
  await page.getByRole("button", { name: "+ Add service" }).click();
  await wait(500);
  await slowType(page.getByPlaceholder("Service name"), "Haircut + Beard");
  await wait(250);
  const dur2 = page.getByPlaceholder("Duration (min)");
  await dur2.click({ clickCount: 3 });
  await dur2.pressSequentially("45", { delay: 55 });
  await wait(250);
  await slowType(page.getByPlaceholder("Price (PHP)"), "250");
  await wait(300);
  await page.getByRole("button", { name: "Add Service" }).click();
  await wait(1500);

  // ── 5. Set hours ───────────────────────────────────────────────────────────
  console.log("[5/8] Set hours");
  await page.getByRole("button", { name: "hours" }).click();
  await wait(800);

  // Enable Monday through Saturday
  // The toggle is the wide pill (w-10 h-6), not the small inner dot (w-4 h-4)
  const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  for (const day of DAYS) {
    // Find the span with the day name, then click the toggle pill beside it
    const toggle = page.locator(`span.w-28:has-text("${day}")`).locator("xpath=preceding-sibling::div").first();
    await toggle.waitFor({ timeout: 5000 });
    await toggle.click();
    await wait(700);
  }
  await wait(1200);

  // ── 6. Profile / Bio ───────────────────────────────────────────────────────
  console.log("[6/8] Profile");
  await page.getByRole("button", { name: "profile" }).click();
  await wait(800);

  await slowType(
    page.locator("textarea"),
    "Walk-in barbershop in Cavite. Fresh cuts, no wait — book ahead to save your spot."
  );
  await wait(600);
  await page.getByRole("button", { name: "Save changes" }).click();
  await wait(1500);

  // ── 7. View booking page ───────────────────────────────────────────────────
  console.log("[7/8] View booking page");
  await page.getByRole("link", { name: "View booking page" }).click();
  await page.waitForLoadState("networkidle");
  await wait(2000);

  // ── 8. Client booking flow ─────────────────────────────────────────────────
  console.log("[8/8] Client books");

  // Pick first service
  await page.getByRole("button", { name: "Haircut" }).first().click();
  await wait(2000);

  // Pick first available date
  const dateBtn = page.locator("button.rounded-2xl").first();
  await dateBtn.waitFor({ timeout: 10000 });
  await dateBtn.click();
  await wait(2000);

  // Pick first available time slot — wait for slots to load
  const slot = page.locator(".grid button").first();
  try {
    await slot.waitFor({ timeout: 10000 });
    await slot.click();
    await wait(2000);
  } catch {
    await page.screenshot({ path: join(OUTPUT_DIR, "debug-slots.png") });
    console.log("  DEBUG: no time slots found. Screenshot saved.");
  }

  // Client details
  const nameInput = page.getByLabel("Your name");
  await nameInput.waitFor({ timeout: 10000 });
  await slowType(nameInput, "Maria Santos");
  await wait(350);
  await slowType(page.getByLabel("Phone number"), "09171234567");
  await wait(800);

  await page.getByRole("button", { name: "Confirm Booking" }).click();
  await wait(3000);

  // ── Done ───────────────────────────────────────────────────────────────────
  console.log("\nDone! Closing browser and saving video...");
  await wait(1500);
  await context.close();
  await browser.close();

  // Rename the auto-named .webm to bookme-demo.webm
  const files = readdirSync(OUTPUT_DIR).filter((f) => f.endsWith(".webm"));
  if (files.length > 0) {
    const latest = files.sort().at(-1);
    renameSync(join(OUTPUT_DIR, latest), join(OUTPUT_DIR, "bookme-demo.webm"));
    console.log("\nVideo saved: tools/bookme-demo/output/bookme-demo.webm");
    console.log("Convert to MP4 with:");
    console.log("  ffmpeg -i output/bookme-demo.webm output/bookme-demo.mp4");
  }
}

main().catch((err) => {
  console.error("\nRecording failed:", err.message);
  process.exit(1);
});
