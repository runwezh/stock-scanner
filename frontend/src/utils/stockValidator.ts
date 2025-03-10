/**
 * 股票代码验证工具
 * 用于验证不同市场类型的股票代码格式
 */

/**
 * 市场类型枚举
 */
export enum MarketType {
  A = 'A',      // A股
  HK = 'HK',    // 港股
  US = 'US',    // 美股
  ETF = 'ETF',  // ETF基金
  LOF = 'LOF'   // LOF基金
}

/**
 * 验证A股股票代码
 * @param code 股票代码
 * @returns 是否为有效的A股代码
 */
export const validateAStock = (code: string): boolean => {
  // 深A主板股票代码00开头，6位数字
  // 中小板股票代码002、003、004开头，6位数字
  // 创业板股票代码300开头，6位数字
  // 沪A主板股票代码600、601、603开头，6位数字
  // 科创板股票代码688开头，6位数字
  // 深B股票代码200开头，6位数字
  // 沪B股票代码900开头，6位数字
  // 老三板A股代码400开头，6位数字
  // 老三板B股代码420开头，6位数字
  // 北京证券交易所股票代码以8开头，一般为5位数字（如80XXX）
  // 股转挂牌股票代码430、830开头，6位数字
  
  // 所有6位数字的股票代码前缀
  const validPrefixes6Digits = [
    '00',   // 深A主板
    '002',  // 中小板
    '003',  // 中小板
    '004',  // 中小板
    '300',  // 创业板
    '600',  // 沪A主板
    '601',  // 沪A主板
    '603',  // 沪A主板
    '688',  // 科创板
    '200',  // 深B股
    '900',  // 沪B股
    '400',  // 老三板A股
    '420',  // 老三板B股
    '430',  // 股转挂牌股票
    '830'   // 股转挂牌股票
  ];
  
  // 验证6位数字的股票代码
  if (/^\d{6}$/.test(code)) {
    for (const prefix of validPrefixes6Digits) {
      if (code.startsWith(prefix)) {
        return true;
      }
    }
  }
  
  // 验证北京证券交易所（以8开头的股票）
  // 北交所股票一般是5位数字，格式为8xxxx
  if (code.startsWith('8') && /^\d{5}$/.test(code)) {
    return true;
  }
  
  return false;
};

/**
 * 验证港股股票代码
 * @param code 股票代码
 * @returns 是否为有效的港股代码
 */
export const validateHKStock = (code: string): boolean => {
  // 港股通常是5位数字
  return /^\d{5}$/.test(code);
};

/**
 * 验证美股股票代码
 * @param code 股票代码
 * @returns 是否为有效的美股代码
 */
export const validateUSStock = (code: string): boolean => {
  // 美股代码通常由字母组成，长度在1-5之间
  return /^[A-Za-z]{1,5}$/.test(code);
};

/**
 * 验证ETF/LOF基金代码
 * @param code 基金代码
 * @returns 是否为有效的基金代码
 */
export const validateFund = (code: string): boolean => {
  // 基金代码通常为6位数字
  return /^\d{6}$/.test(code);
};

/**
 * 根据市场类型验证股票代码
 * @param code 股票代码
 * @param marketType 市场类型
 * @returns 包含验证结果和错误信息的对象
 */
export const validateStockCode = (
  code: string, 
  marketType: MarketType
): { valid: boolean; errorMessage?: string } => {
  
  if (!code || code.trim() === '') {
    return { 
      valid: false, 
      errorMessage: '股票代码不能为空' 
    };
  }
  
  switch (marketType) {
    case MarketType.A:
      if (!validateAStock(code)) {
        return { 
          valid: false, 
          errorMessage: `无效的A股股票代码格式: ${code}。支持的代码格式包括：深A主板(00)、中小板(002/003/004)、创业板(300)、沪A主板(600/601/603)、科创板(688)、深B股(200)、沪B股(900)、老三板(400/420)、北交所(8开头5位数)、股转系统(430/830)`
        };
      }
      break;
      
    case MarketType.HK:
      if (!validateHKStock(code)) {
        return { 
          valid: false, 
          errorMessage: `无效的港股代码格式: ${code}。港股代码应为5位数字` 
        };
      }
      break;
      
    case MarketType.US:
      if (!validateUSStock(code)) {
        return { 
          valid: false, 
          errorMessage: `无效的美股代码格式: ${code}。美股代码应为1-5位字母` 
        };
      }
      break;
      
    case MarketType.ETF:
    case MarketType.LOF:
      if (!validateFund(code)) {
        return { 
          valid: false, 
          errorMessage: `无效的${marketType}基金代码格式: ${code}。基金代码应为6位数字` 
        };
      }
      break;
      
    default:
      return { 
        valid: false, 
        errorMessage: `不支持的市场类型: ${marketType}` 
      };
  }
  
  return { valid: true };
};

/**
 * 批量验证多个股票代码
 * @param codes 股票代码数组
 * @param marketType 市场类型
 * @returns 包含所有无效代码及其错误信息的数组
 */
export const validateMultipleStockCodes = (
  codes: string[], 
  marketType: MarketType
): { code: string; errorMessage: string }[] => {
  const invalidCodes: { code: string; errorMessage: string }[] = [];
  
  for (const code of codes) {
    const result = validateStockCode(code, marketType);
    if (!result.valid && result.errorMessage) {
      invalidCodes.push({
        code,
        errorMessage: result.errorMessage
      });
    }
  }
  
  return invalidCodes;
};