export async function insertText(text: string) {
  try {
    await Excel.run(async (context) => {
      const sheet = context.workbook.worksheets.getActiveWorksheet();
      
      // 获取当前选中的范围，如果没有选中则使用 A1
      let range;
      try {
        range = context.workbook.getSelectedRange();
      } catch {
        // 如果没有选中范围，使用 A1
        range = sheet.getRange("A1");
      }
      
      // 如果是公式（以 = 开头），则设置公式
      if (text.startsWith('=')) {
        range.formulas = [[text]];
      } else {
        // 否则设置为普通文本
        range.values = [[text]];
      }
      
      range.format.autofitColumns();
      await context.sync();
    });
  } catch (error) {
    console.log("Error: " + error);
    throw error; // 重新抛出错误以便上层处理
  }
}
