import requests, threading, time, os
from utils.logger import logger
from proxy.scrape_proxy import ProxyStore

proxy_store = ProxyStore()


class SuiFaucet:
    def __init__(self) -> None:
        pass

    def run_sui_faucet(self, address):
        proxy = proxy_store.random_proxy
        if not proxy:
            logger.error(f"{address} Faucet: no valid proxy")
            return
        type, ip, port = proxy["type"], proxy["ip"], proxy["port"]
        if type == "http":
            proxy_url = f"http://{ip}:{port}"
        elif type == "socks5":
            proxy_url = f"socks5://{ip}:{port}"
        elif type == "socks4":
            proxy_url = f"socks4://{ip}:{port}"
        elif type == "https":
            proxy_url = f"socks4://{ip}:{port}"
        proxies = {"http": proxy_url, "https": proxy_url}

        try:
            r = requests.post(
                "https://faucet.testnet.sui.io/v1/gas",
                headers={
                    "Content-Type": "application/json",
                },
                json={
                    "FixedAmountRequest": {
                        "recipient": address,
                    }
                },
                proxies=proxies,
                timeout=10,
                verify=False,
            )
            logger.info(
                f"{address} Faucet: using proxy {proxy_url} {r.status_code} {r.text}"
            )
            r.raise_for_status()
        except Exception as e:
            logger.warning(f"Remove proxy {proxy_url}")
            proxy_store.remove_proxy(ip)
            logger.error(f"{address} Faucet using proxy {proxy_url}: {e}")

    def run(self, chunk_size=10):
        while True:
            wallet_txt_file = "sui_wallets.txt"
            if not os.path.exists(wallet_txt_file):
                logger.error(f"{wallet_txt_file} not found")
                return
            wallets = [
                line.strip()
                for line in open(wallet_txt_file, "r").readlines()
                if line.strip()
            ]
            chunks = [
                wallets[i : i + chunk_size] for i in range(0, len(wallets), chunk_size)
            ]
            for chunk in chunks:
                threads = []
                for wallet in chunk:
                    t = threading.Thread(
                        target=self.run_sui_faucet,
                        args=(wallet,),
                    )
                    threads.append(t)
                for t in threads:
                    t.start()
                for t in threads:
                    t.join()
