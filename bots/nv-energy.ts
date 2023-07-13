import type { WebDriver } from "selenium-webdriver";
import { By, Key, until } from "selenium-webdriver";
import {
  BotRunStatus,
  isWebElementPresent,
  locateFieldById,
  locateFieldByXpath,
  openAndMaximizeWebpage,
  sleep,
} from "../utils";

export async function login(driver: WebDriver, username: string, password: string) {
  // login
  await openAndMaximizeWebpage(driver, "https://www.nvenergy.com/");
  await sleep(20000);
  await driver.wait(until.elementLocated(By.xpath(`//button[@aria-label="Log In"]`))).click();
  await sleep(15000);
  const userIdField = await locateFieldById(driver, "signInName");
  await userIdField.sendKeys(username, Key.TAB, password, Key.ENTER);
  await sleep(15000);
  await isWebElementPresent(
    driver,
    By.className("current-bill-tile-component"),
    BotRunStatus.FAILED_LOGIN
  );
}

export async function fetchPDF(driver: WebDriver) {
  const pdfButton = await driver.wait(until.elementLocated(By.css("#dwnldLnk a")));
  await pdfButton.click();
  await sleep(5000);
}

export async function validateCredentials(driver: WebDriver) {
  const promise1 = driver
    .wait(until.elementLocated(By.id(`current-bill-tile-component`)))
    .then(() => true);

  const promise2 = driver
    .wait(until.elementLocated(By.className("sign-in-error")))
    .then(() => false);

  const promiseValue = await Promise.race([promise1, promise2]);
  return promiseValue || false;
}

export async function returnWebBalance(driver: WebDriver) {
  await sleep(5000);
  const promise = await locateFieldByXpath(driver, `//div[@class="panel-body"]/div/div/div/span`);

  const balance = (await promise.getText()).split("$");
  if (balance[0] === "-") {
    return parseFloat(balance[1]) * -1;
  }
  return parseFloat(balance[1]);
}

export default {
  login,
  fetchPDF,
  validateCredentials,
  returnWebBalance,
};
