// Run through the supported CUA session with its existing local preview tab.
// No separate browser launch or provider requests.
import assert from 'node:assert/strict';

export async function checkLanding(tab) {
  const results = [];
  const check = (name, condition) => { assert.ok(condition, name); results.push(name); };
  await tab.reload();
  await tab.playwright.domSnapshot();
  const open = tab.playwright.getByRole('button', {name: 'Open navigation', exact: true});
  const dialog = tab.playwright.getByRole('dialog', {name: 'Navigation'});
  const close = tab.playwright.getByRole('button', {name: 'Close navigation'});
  await open.click();
  await tab.playwright.domSnapshot();
  check('Logo opens the navigation dialog', await dialog.isVisible());
  check('Open state is announced', await open.getAttribute('aria-expanded') === 'true');
  await close.press('Shift+Tab');
  check('Backward tab stays inside drawer', await tab.playwright.evaluate(() =>
    document.activeElement.textContent.trim().includes('View source')));
  await dialog.getByRole('link', {name: 'View source'}).press('Tab');
  check('Forward tab returns to drawer close', await tab.playwright.evaluate(() =>
    document.activeElement.getAttribute('aria-label') === 'Close navigation'));
  await close.press('Escape');
  await tab.playwright.domSnapshot();
  check('Escape dismisses navigation', !(await dialog.isVisible()));
  check('Dismissal returns focus to opener', await tab.playwright.evaluate(() =>
    document.activeElement.getAttribute('aria-label') === 'Open navigation'));
  await open.click();
  await tab.playwright.domSnapshot();
  await dialog.getByRole('link', {name: 'How it works'}).click();
  await tab.playwright.domSnapshot();
  check('Section navigation dismisses drawer', !(await dialog.isVisible()));
  check('Section navigation targets the workflow', (await tab.url()).endsWith('#workflow'));
  check('Section navigation moves keyboard focus', await tab.playwright.evaluate(() =>
    document.activeElement.id === 'workflow'));
  const details = tab.playwright.locator('.voice-evidence summary');
  await details.click();
  await tab.playwright.domSnapshot();
  check('Real voice evidence is expandable', await tab.playwright.evaluate(() =>
    document.querySelector('.voice-evidence').open));
  await details.click();
  await tab.playwright.domSnapshot();
  check('Evidence can be collapsed', await tab.playwright.evaluate(() =>
    !document.querySelector('.voice-evidence').open));
  const integrity = await tab.playwright.evaluate(() => ({
    anchors: [...document.querySelectorAll('a[href^="#"]')].every(a =>
      !!document.getElementById(a.getAttribute('href').slice(1))),
    noFakePlayer: document.querySelectorAll('video, audio').length === 0 &&
      document.querySelector('.video-note').textContent.includes('Recording is pending'),
    noOverflow: document.documentElement.scrollWidth <= innerWidth,
  }));
  check('All section links resolve', integrity.anchors);
  check('Unavailable video is honestly represented', integrity.noFakePlayer);
  check('No horizontal overflow', integrity.noOverflow);
  return results;
}
