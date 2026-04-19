import requests, re, os, ipaddress, socket, time
from bs4 import BeautifulSoup
import concurrent.futures
import urllib3

# 禁用未验证 HTTPS 请求的警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 基础配置 =================
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# ================= 测速参数配置 =================
# 阶段一：TCP 延迟测速
TEST_PORT = 443
PING_TIMEOUT = 1.0          # Ping 超时时间(秒)
MAX_PING_WORKERS = 200      # Ping 并发数

# 阶段二：真实下载测速
DOWNLOAD_TEST_COUNT = 50    # 只对延迟最低的前 50 个 IP 测速
DOWNLOAD_TIMEOUT = 5.0      # 下载测试掐断时间(秒) - 已修改为 5s
MAX_DL_WORKERS = 3          # 下载测速并发数 - 已修改为 3
TEST_FILE_SIZE = 500 * 1024 * 1024 # 测试文件大小 - 已修改为 500MB
TEST_HOST = "speed.cloudflare.com" # 伪造的 Host 头

# ================= 1. 原始 URL 数据源 =================
sources = {
    'https://api.uouin.com/cloudflare.html': 'Uouin',
    'https://ip.164746.xyz': 'ZXW',
    'https://ipdb.api.030101.xyz/?type=bestcf': 'IPDB',
    'https://cf.090227.xyz/CloudFlareYes': 'CFYes',
    'https://ip.haogege.xyz': 'HaoGG',
    'https://vps789.com/openApi/cfIpApi': 'VPS',
    'https://www.wetest.vip/page/cloudflare/address_v4.html': 'WeTest',
    'https://addressesapi.090227.xyz/ct': 'CMLiuss',
    'https://raw.githubusercontent.com/xingpingcn/enhanced-FaaS-in-China/refs/heads/main/Cf.json': 'FaaS'
}

# ================= 2. 完整的域名列表 =================
domain_list = [
    "links1.cloudflare.com", "www.indutrade.se", "jackcraft.cn", "cfcname.cdn.urlce.com",
    "cfcdn.api.urlce.com", "singgcdn.singgnetworkcdn.com", "coori.cloudflareaccess.com",
    "staticdelivery.nexusmods.com", "www.nexusmods.com", "store.ubi.com", "ssh.awcode.cn",
    "cfyx.aliyun.20237737.xyz", "openai.com", "www.mnn.tw", "blog.646474.xyz",
    "www.skillshare.com", "cf.130519.xyz", "www.mofanghao.com", "www.securitybank.com",
    "www.sdgggo.com", "blog.811520.xyz", "www.colamanga.com", "cloudflare-ech.com",
    "www.hostuno.com", "www.serv00.com", "expireddomains.com", "www.dotdotnetworks.com",
    "www.lmu5.com", "www.wrangler.com", "www.entrust.com", "www.vitafoodsglobal.com",
    "www.softswiss.com", "www.hostgator.com", "www.ubykotex.com", "www.uts.edu.au",
    "www.baxterford.com", "www.usphonebook.com", "www.hog.com", "www.harley-davidson.com",
    "www.dbs.com", "www.dbs.com.sg", "www.cerave.uy", "www.olukai.com", "www.maybelline.de",
    "www.secretsales.com", "www.starbucks.co.uk", "polestar.com", "www.casetify.com",
    "casetify.com", "goremountain.com", "www.qualcomm.com", "hostinger.in", "cf.636949.xyz",
    "cf.877774.xyz", "kirssr.fun", "cloudflare-dns.com", "cdns.doon.eu.org",
    "www.cloudflare-dns.com", "openapi.973973.xyz", "sheetdb.io", "www.shopify.com",
    "mfa.gov.ua", "dnb.com.sg", "widget.time.is", "www.freedidi.com", "usa.visa.com",
    "saas.sin.fan", "cloudflare.cdnjson.com", "cmcc.877774.xyz", "ct.877774.xyz",
    "ks5555555.com", "pete.ns.cloudflare.com", "ken.ns.cloudflare.com", "tani.ns.cloudflare.com",
    "toby.ns.cloudflare.com", "evangeline.ns.cloudflare.com", "fonzie.ns.cloudflare.com",
    "henrik.ns.cloudflare.com", "lola.ns.cloudflare.com", "alla.ns.cloudflare.com",
    "kipp.ns.cloudflare.com", "josh.ns.Cloudflare.com", "rayne.ns.cloudflare.com",
    "dorthy.ns.cloudflare.com", "vern.ns.cloudflare.com", "alec.ns.cloudflare.com",
    "kate.ns.cloudflare.com", "princess.ns.cloudflare.com", "magali.ns.cloudflare.com",
    "damon.ns.cloudflare.com", "kara.ns.cloudflare.com", "www.moodys.com", "www.sapaad.com",
    "cdn.netflixgc.xyz", "www.worldlearning.org", "bestcf.030101.xyz", "1357900.xyz",
    "dm84.net", "freeyx.cloudflare88.eu.org", "cfip.huangbin.net", "cdn1.5118cl0ud.xyz",
    "e.download.yunzhongzhuan.com", "www.zmsub.top", "www.speedtest.net", "ips.993888.xyz",
    "whatismyipaddress.com", "ip.skk.moe", "www.visa.com.hk", "www.visa.com.sg",
    "www.visa.com.tw", "www.visa.com.mt", "www.visa.co.id", "www.visa.co.ke",
    "www.visa.co.in", "www.visa.ca", "www.visa.com.ai", "africa.visa.com",
    "caribbean.visa.com", "pages.dev", "store.epicgames.com", "www.epicgames.com",
    "www.fortnite.com", "visaeurope.at", "qa.visamiddleeast.com", "time.is", "www.wto.org",
    "icook.hk", "icook.tw", "visamiddleeast.com", "portal.cloudflarepartners.com",
    "support.cloudflarewarp.com", "developers.cloudflare.com", "ai.cloudflare.com",
    "try.cloudflare.com", "blog.cloudflare.com", "community.cloudflare.com",
    "abuse.cloudflare.com", "sso.cloudflare.dev", "ns5.cloudflare.com", "ns6.cloudflare.com",
    "ns7.cloudflare.com", "ns3.cloudflare.com", "ns4.cloudflare.com", "workers.cloudflare.com",
    "radar.cloudflare.com", "support.cloudflare.com", "challenge.developers.cloudflare.com",
    "pages.cloudflare.com", "ns.cloudflare.com", "arena.lmsys.org", "lmarena.ai",
    "platform.dash.cloudflare.com", "info.cloudflare.com", "sparrow.cloudflare.com",
    "videodelivery.net", "www.csgo.com", "digitalocean.com", "www.dynadot.com",
    "singapore.com", "ping.pe", "store.ubisoft.com", "users.nexusmods.com",
    "wall.alphacoders.com", "www.alphacoders.com", "www.hcaptcha.com", "www.wemod.com",
    "faceit-client.faceit-cdn.net", "anticheat-client.faceit-cdn.net",
    "download-alt.easyanticheat.net", "www.namesilo.com", "www.fontawesome.com",
    "ajax.cdnjs.com", "uptimerobot.com", "opencollective.com", "www.hostpapa.in",
    "www.hyva.com", "www.hostinger.com", "www.namecheap.com", "www.netim.com",
    "www.spaceship.com", "www.domain.com", "www.epik.com", "malaysia.com",
    "ae.visamiddleeast.com", "www.geolocation.com", "www.4chan.org", "customer.l53.net",
    "www.coleman.com", "graylog.org", "david.ns.cloudflare.com", "june.ns.cloudflare.com",
    "www.ipxo.com", "cdnjs.com", "www.racknerd.com", "pkg.cloudflare.com",
    "discord.cloudflare.com", "crypto.cloudflare.com", "migp.cloudflare.com",
    "api.radar.cloudflare.com", "r2-calculator.cloudflare.com", "rpki.cloudflare.com",
    "performance.radar.cloudflare.com", "dash.teams.cloudflare.com", "one.dash.cloudflare.com",
    "static.cloudflareinsights.com", "geolocation.onetrust.com", "gates.cloudflare.com",
    "research.cloudflare.com", "partners.cloudflare.com", "peering.cloudflare.com",
    "malcolm.cloudflare.com", "deploy.workers.cloudflare.com", "opaque.research.cloudflare.com",
    "teams.cloudflare.com", "ct.cloudflare.com", "cn.cloudflare.com", "drand.cloudflare.com",
    "classic.radar.cloudflare.com", "privacypass.cloudflare.com", "content.cloudflare.com",
    "opaque-full.research.cloudflare.com", "icons.getbootstrap.com", "blog.getbootstrap.com",
    "cloudflare.tv", "cloudflaretv.cloudflareaccess.com", "staging.cloudflare.tv",
    "cloudflare.tv.cdn.cloudflare.net", "www.cloudflare.tv.cdn.cloudflare.net",
    "staging.cloudflare.tv.cdn.cloudflare.net", "live.cloudflare.tv.cdn.cloudflare.net",
    "www.cloudflare.tv", "radar-cfdata-org.cloudflareaccess.com", "isbgpsafeyet.com",
    "anycast.com", "cffast.wawacm.com", "cfcnc.cdnddd.com", "dos-op.io", "www.noi.org",
    "www.89d.com", "download.redis.io", "www.vitagreen.com", "www.h5.com",
    "www.pacopacomama.com", "packages.adoptium.net", "haven1.tokensoft.io",
    "binary.lge.modcdn.io", "nexusmods.com", "www.it7.net"
]

ipv4_set = set()

def process_ip(ip):
    """验证并存储纯 IPv4"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback: return
        if ip_obj.version == 4:
            ipv4_set.add(str(ip_obj))
    except:
        pass

# ================= 核心工作库 =================

def check_ip_latency(ip):
    """阶段一：TCP 延迟测试"""
    start_time = time.time()
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(PING_TIMEOUT)
            s.connect((ip, TEST_PORT))
        return ip, (time.time() - start_time) * 1000
    except:
        return ip, None

def run_ping_test(ip_set):
    """多线程并发执行 Ping 测试"""
    print(f"\n🚀 [阶段一] 开始测试 {len(ip_set)} 个 IPv4 节点的 TCP 延迟...")
    valid_ips = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_PING_WORKERS) as executor:
        futures = {executor.submit(check_ip_latency, ip): ip for ip in ip_set}
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            ip, latency = future.result()
            if latency is not None:
                valid_ips.append((ip, latency))
            print(f"\r进度: {completed}/{len(ip_set)} | 发现可用节点: {len(valid_ips)} 个", end="")
    print()
    valid_ips.sort(key=lambda x: x[1])
    return valid_ips

def check_download_speed(ip_data):
    """阶段二：真实 HTTP 下载测速"""
    ip, latency = ip_data
    url = f"https://{ip}/__down?bytes={TEST_FILE_SIZE}"
    
    headers = {'Host': TEST_HOST, 'User-Agent': HEADERS['User-Agent']}
    start_time = time.time()
    downloaded_bytes = 0
    
    try:
        # verify=False 忽略证书警告，允许 IP 直连
        r = requests.get(url, headers=headers, stream=True, timeout=PING_TIMEOUT, verify=False)
        r.raise_for_status()
        
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                downloaded_bytes += len(chunk)
            if time.time() - start_time > DOWNLOAD_TIMEOUT:
                break
                
        time_spent = time.time() - start_time
        speed_mbps = (downloaded_bytes / time_spent) / (1024 * 1024)
        return ip, latency, speed_mbps
    except Exception:
        return ip, latency, 0.0

def run_download_test(ping_sorted_ips):
    """多线程并发执行下载测速"""
    targets = ping_sorted_ips[:DOWNLOAD_TEST_COUNT]
    if not targets: return []
    
    print(f"\n🚀 [阶段二] 开始对延迟最低的 {len(targets)} 个 IPv4 节点进行真实下载测速...")
    print(f"参数: 500MB文件 | {DOWNLOAD_TIMEOUT}秒强制结束 | {MAX_DL_WORKERS}并发")
    final_results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_DL_WORKERS) as executor:
        futures = {executor.submit(check_download_speed, item): item for item in targets}
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            completed += 1
            ip, latency, speed = future.result()
            if speed > 0:
                final_results.append((ip, latency, speed))
            print(f"\r进度: {completed}/{len(targets)} | 测出高带宽节点: {len(final_results)} 个", end="")
            
    print()
    final_results.sort(key=lambda x: x[2], reverse=True)
    return final_results

# ================= 主程序执行 =================

# 1. 从域名列表解析 IP
print(f"🔄 正在从 {len(domain_list)} 个域名中解析 IP...")
for dom in list(set(domain_list)):
    try:
        addrs = socket.getaddrinfo(dom, None)
        for a in addrs:
            process_ip(a[4][0])
    except:
        continue

# 2. 从 URL 源抓取 IP
ipv4_re = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

for url, name in sources.items():
    print(f"🌐 正在抓取源: {name}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        content = r.text if url.endswith('.txt') else BeautifulSoup(r.text, 'html.parser').get_text()
        for ip in re.findall(ipv4_re, content): process_ip(ip)
    except:
        print(f"⚠️ 跳过源 {name}")

# 3. 阶段一：执行 TCP 测试
tested_ipv4 = run_ping_test(ipv4_set)

# 4. 阶段二：执行真实下载测速
final_ipv4 = run_download_test(tested_ipv4)

# 5. 保存结果
filename = 'ipv4_premium.txt'
print(f"\n💾 正在保存优选结果...")
if os.path.exists(filename): os.remove(filename)
with open(filename, 'w', encoding='utf-8') as f:
    f.write("IP地址, TCP延迟(ms), 下载速度(MB/s)\n")
    for ip, latency, speed in final_ipv4:
        f.write(f"{ip}, {latency:.2f}, {speed:.2f}\n")

print(f"\n✅ 全部处理完成！最终测出的 IPv4 优选节点已保存至: {filename}")
