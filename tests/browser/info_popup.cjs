// Po zainstalowaniu Playwright i Chromium uruchom test na lokalnym podglądzie 3D.
// node --test tests/browser/info_popup.cjs
const assert = require('node:assert/strict');
const {test} = require('node:test');
const {chromium, devices} = require('playwright');

const url = process.env.JKTZ_VIEWER_URL || 'http://127.0.0.1:8080/';

async function withViewer(options, check) {
    const browser = await chromium.launch({
        executablePath: process.env.JKTZ_CHROMIUM_PATH,
        args: ['--enable-unsafe-swiftshader'],
    });
    try {
        const page = await browser.newPage(options);
        await page.goto(url);
        await check(page);
    } finally {
        await browser.close();
    }
}

test('stuknięcie w model zamyka okno informacyjne', async () => {
    await withViewer({...devices['Pixel 7'], deviceScaleFactor: 1}, async page => {
        const popup = page.locator('#info-popup');
        const button = page.locator('.info-btn');
        const canvas = page.locator('#viewer canvas');

        assert.equal(await popup.isVisible(), true);
        await popup.locator('.title').tap();
        assert.equal(await popup.isVisible(), true);

        await canvas.tap();
        assert.equal(await popup.isVisible(), false, 'okno pozostało otwarte po stuknięciu w model');

        await button.tap();
        assert.equal(await popup.isVisible(), true);
        await button.tap();
        assert.equal(await popup.isVisible(), false);
    });
});

test('kliknięcie myszą w model zamyka okno informacyjne', async () => {
    await withViewer({}, async page => {
        const popup = page.locator('#info-popup');

        assert.equal(await popup.isVisible(), true);
        await page.locator('#viewer canvas').click();
        assert.equal(await popup.isVisible(), false);
    });
});
