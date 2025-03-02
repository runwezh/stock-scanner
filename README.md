# 股票分析系统 (Stock Analysis System)

## 简介
基于 https://github.com/DR-lin-eng/stock-scanner 二次修改，感谢原作者

## 功能变更
1. 增加html页面，支持浏览器在线使用。
2. 增加港股、美股支持。
3. 完善Dockerfile、GitHub Actions 支持docker一键部署使用。
4. 支持x86_64 和 ARM64架构镜像

## docker一键部署
```
docker run -d \
  --name stock-scanner \
  -p 8888:8888 \
  -e GEMINI_API_KEY=替换为你的key \
  -e GEMINI_API_URL=替换为你的api地址 \
  -e GEMINI_API_MODEL=替换为你的模型 \
  lanzhihong/stock-scanner:latest
```
默认8888端口，部署完成后访问  http://127.0.0.1:8888 即可使用。


## 注意事项 (Notes)
- 股票分析仅供参考，不构成投资建议
- 使用前请确保网络连接正常
- 建议在实盘前充分测试

## 贡献 (Contributing)
欢迎提交 issues 和 pull requests！

## 许可证 (License)
[待添加具体许可证信息]

## 免责声明 (Disclaimer)
本系统仅用于学习和研究目的，投资有风险，入市需谨慎。
