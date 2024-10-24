import requests, time, traceback, threading, os, json, random
from utils.logger import logger

home_dir = os.path.expanduser("~")
proxies_dir = os.path.join(home_dir, ".farmbot", "proxies")

if not os.path.exists(proxies_dir):
    os.makedirs(proxies_dir, exist_ok=True)


class ProxyStore:
    @property
    def random_proxy(self):
        files = os.listdir(proxies_dir)
        if not files:
            return None
        proxies_json_file = os.path.join(proxies_dir, random.choice(files))
        with open(proxies_json_file, "r") as f:
            return json.load(f)

    def save_proxy(self, type, ip, port) -> bool:
        filename = os.path.join(proxies_dir, f"{ip}.json")
        if os.path.exists(filename):
            return False

        with open(filename, "w") as f:
            json.dump({"ip": ip, "port": port, "type": type}, f)

        return True

    def remove_proxy(self, ip):
        filename = os.path.join(proxies_dir, f"{ip}.json")
        if os.path.exists(filename):
            os.remove(filename)

    def get_proxy_count(self):
        return len(os.listdir(proxies_dir))


class ProxyScraper:

    def __init__(self) -> None:
        self.proxy_store = ProxyStore()

    def scrape_form_geonode(self):
        logger.info("Scrape proxy from geonode")
        page = 1
        page_size = 500
        while True:
            api = f"https://proxylist.geonode.com/api/proxy-list?limit={page_size}&page={page}&sort_by=lastChecked&sort_type=desc"
            response = requests.get(api)
            data = response.json()
            total = data["total"]
            # 判断是否还有下一页
            if page * page_size >= total:
                break
            page += 1
            for item in data["data"]:
                ip = item["ip"]
                port = int(item["port"])
                protocols = item["protocols"]
                type = protocols[0]
                created = self.proxy_store.save_proxy(type, ip, port)
                if created:
                    logger.info(f"成功添加代理: {type}://{ip}:{port}")

            time.sleep(1)

    def scrape_form_geonode_forever(self):
        while True:
            try:
                self.scrape_form_geonode()
            except Exception as e:
                traceback.format_exc()
            finally:
                time.sleep(60)

    def scrape_from_proxyscrape(
        self,
    ):
        logger.info("Scrape proxy from proxyscrape")
        api = "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=json"
        response = requests.get(api)
        data = response.json()
        proxies = data["proxies"]
        for proxy in proxies:
            alive, ip, port, type, ip_data = (
                proxy["alive"],
                proxy["ip"],
                proxy["port"],
                proxy["protocol"],
                proxy["ip_data"],
            )
            if not alive:
                continue
            created = self.proxy_store.save_proxy(type, ip, port)
            if created:
                logger.info(f"成功添加代理: {type}://{ip}:{port}")

    def scrape_from_proxyscrape_forever(self):
        while True:
            try:
                self.scrape_from_proxyscrape()
            except Exception as e:
                traceback.format_exc()
            finally:
                time.sleep(60)

    def scrape_from_github_TheSpeedX(self):
        logger.info("Scrape proxy from github TheSpeedX")
        http_api = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/refs/heads/master/http.txt"
        socks4_api = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/refs/heads/master/socks4.txt"
        socks5_api = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/refs/heads/master/socks5.txt"

        apis = [http_api, socks4_api, socks5_api]
        for api in apis:
            response = requests.get(api)
            data = response.text
            for line in data.split("\n"):
                line = line.strip()
                if not line:
                    continue
                ip, port = line.split(":")
                port = int(port)
                type = api.split("/")[-1].split(".")[0]
                created = self.proxy_store.save_proxy(type, ip, port)
                if created:
                    logger.info(f"成功添加代理: {ip}:{port}")

    def scrape_from_github_TheSpeedX_forever(self):
        while True:
            try:
                self.scrape_from_github_TheSpeedX()
            except Exception as e:
                traceback.format_exc()
            finally:
                time.sleep(3600)

    def scrape_from_github_proxifly(self):
        logger.info("Scrape proxy from github proxifly")
        url = "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/all/data.json"
        r = requests.get(url)
        data = r.json()
        for item in data:
            ip = item["ip"]
            port = item["port"]
            type = item["protocol"]
            created = self.proxy_store.save_proxy(type, ip, port)
            if created:
                logger.info(f"成功添加代理: {type}://{ip}:{port}")

    def scrape_from_github_proxifly_forever(self):
        while True:
            try:
                self.scrape_from_github_proxifly()
            except Exception as e:
                traceback.format_exc()
            finally:
                time.sleep(3600)

    def monitor_proxy_count(self):
        while True:
            count = self.proxy_store.get_proxy_count()
            logger.info(f"当前代理数量: {count}")
            time.sleep(60)

    def run(self):
        threads = [
            threading.Thread(target=self.scrape_form_geonode_forever),
            threading.Thread(target=self.scrape_from_proxyscrape_forever),
            threading.Thread(target=self.scrape_from_github_TheSpeedX_forever),
            threading.Thread(target=self.scrape_from_github_proxifly_forever),
            threading.Thread(target=self.monitor_proxy_count),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
