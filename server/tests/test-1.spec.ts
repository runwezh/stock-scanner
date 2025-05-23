import { test, expect } from '@playwright/test';

test('test', async ({ page }) => {
  test.setTimeout(120000); // 可选，延长测试用例超时
  await page.goto('http://localhost/#/login');
  await page.getByRole('textbox', { name: '请输入用户名' }).click();
  await page.getByRole('textbox', { name: '请输入用户名' }).fill('cocodady');
  await page.getByRole('textbox', { name: '请输入密码' }).click();
  await page.getByRole('textbox', { name: '请输入密码' }).fill('761126a8');
  await page.getByRole('button', { name: '登 录' }).click();
  await page.getByRole('textbox', { name: '输入股票、基金代码，多个代码用逗号、空格或换行分隔' }).click();
  await page.getByRole('textbox', { name: '输入股票、基金代码，多个代码用逗号、空格或换行分隔' }).fill('000001');
  await page.getByRole('button', { name: '开始分析' }).click();

  // 只要页面上出现"平安银行"四个字即可
  await expect(page.getByText(/平安银行/)).toBeVisible({ timeout: 30000 });
});