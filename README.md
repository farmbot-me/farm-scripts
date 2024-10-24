# Farm Bot - Web3 撸毛脚本

## 运行

### 安装依赖

```sh
pip install -r requirements.txt
```

### 运行脚本

脚本的入口文件以 `entry_xxxx.py` 命名，可以直接使用 Python 运行。

## 脚本列表

### 批量抓取免费代理

> 从 geonode, proxyscrape 以及一些公开的 GitHub 仓库抓取代理到本地。默认的代理数据保存目录为 `~/.farmbot/proxies/`。

```sh
python entry_scrape_proxy.py
```

### SUI 测试网自动领水

> 使用官方的 `https://faucet.testnet.sui.io/v1/gas` 接口进行领水，一个地址一天最多只能领两次水，同时同一个 IP 会有频率限制。此脚本会使用上一步抓到的代理自动领水，如果领水失败会将代理移除，再尝试使用其他的 IP。

在项目的路径下创建 `sui_wallets.txt` 文件，添加 SUI 钱包地址，一行一个。

然后运行：

```
python entry_sui_faucet.py
```
