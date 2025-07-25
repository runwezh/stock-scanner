/**
 * 股票代码验证工具
 * 用于验证不同市场类型的股票代码格式
 */

/**
 * 市场类型枚举
 */
export enum MarketType {
	A = "A", // A股
	HK = "HK", // 港股
	US = "US", // 美股
	ETF = "ETF", // ETF基金
	LOF = "LOF", // LOF基金
}

/**
 * 验证A股股票代码
 * @param code 股票代码
 * @returns 是否为有效的A股代码
 */
export const validateAStock = (code: string): boolean => {
	// A股代码验证规则：
	// 沪市主板：600、601、603、605开头
	// 深市主板：000-002开头
	// 创业板：300开头
	// 科创板：688开头
	// 北交所：8开头（83、87、88等）和920开头
	// 新三板：4开头（400、430等）
	return /^(60[0135]\d{3}|0[0-2]\d{4}|30\d{4}|688\d{3}|[48]\d{5}|920\d{3})$/.test(
		code,
	);
};

/**
 * 验证港股股票代码
 * @param code 股票代码
 * @returns 是否为有效的港股代码
 */
export const validateHKStock = (code: string): boolean => {
	// 支持可选的HK前缀，后跟3~5位数字
	return /^([Hh][Kk])?\d{3,5}$/.test(code);
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
	marketType: MarketType,
): { valid: boolean; errorMessage?: string } => {
	if (!code || code.trim() === "") {
		return {
			valid: false,
			errorMessage: "股票代码不能为空",
		};
	}

	switch (marketType) {
		case MarketType.A:
			if (!validateAStock(code)) {
				return {
					valid: false,
					errorMessage: `无效的A股代码格式: ${code}。支持格式：沪市主板(600、601、603、605开头)、深市主板(000-002开头)、创业板(300开头)、科创板(688开头)、北交所(8开头或920开头)、新三板(4开头)`,
				};
			}
			break;

		case MarketType.HK:
			if (!validateHKStock(code)) {
				return {
					valid: false,
					errorMessage: `无效的港股代码格式: ${code}。港股代码应为3-5位数字或HK开头`,
				};
			}
			break;

		case MarketType.US:
			if (!validateUSStock(code)) {
				return {
					valid: false,
					errorMessage: `无效的美股代码格式: ${code}。美股代码应为1-5位字母`,
				};
			}
			break;

		case MarketType.ETF:
		case MarketType.LOF:
			if (!validateFund(code)) {
				return {
					valid: false,
					errorMessage: `无效的${marketType}基金代码格式: ${code}。基金代码应为6位数字`,
				};
			}
			break;

		default:
			return {
				valid: false,
				errorMessage: `不支持的市场类型: ${marketType}`,
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
	marketType: MarketType,
): { code: string; errorMessage: string }[] => {
	const invalidCodes: { code: string; errorMessage: string }[] = [];

	for (const code of codes) {
		const result = validateStockCode(code, marketType);
		if (!result.valid && result.errorMessage) {
			invalidCodes.push({
				code,
				errorMessage: result.errorMessage,
			});
		}
	}

	return invalidCodes;
};
