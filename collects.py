import requests, re, os, ipaddress, socket, time
import concurrent.futures
from bs4 import BeautifulSoup

# ✅ 基础配置
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
MAX_WORKERS_DNS = 20  # DNS 解析并发数
MAX_WORKERS_HTTP = 10 # 网页抓取并发数
POLL_TIMES = 5        # DNS 轮询榨干次数

# ✅ 1. 原始 URL 数据源
sources = {
    'https://api.uouin.com/cloudflare.html': 'Uouin',
    'https://ip.164746.xyz': 'ZXW',
    'https://ipdb.api.030101.xyz/?type=bestcf': 'IPDB',
    'https://www.wetest.vip/page/cloudflare/address_v6.html': 'WeTestV6',
    'https://ipdb.api.030101.xyz/?type=bestcfv6': 'IPDBv6',
    'https://cf.090227.xyz/CloudFlareYes': 'CFYes',
    'https://ip.haogege.xyz': 'HaoGG',
    'https://vps789.com/openApi/cfIpApi': 'VPS',
    'https://www.wetest.vip/page/cloudflare/address_v4.html': 'WeTest',
    'https://addressesapi.090227.xyz/ct': 'CMLiuss',
    'https://addressesapi.090227.xyz/cmcc-ipv6': 'CMLiussv6',
    'https://raw.githubusercontent.com/xingpingcn/enhanced-FaaS-in-China/refs/heads/main/Cf.json': 'FaaS'
}

# ✅ 2. 完整的域名列表
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

# 全局存储结果 (在 Python 中 set.add 是原子的，多线程安全)
ipv4_set = set()
ipv6_set = set()

def process_ip(ip):
    """验证并存储纯 IP"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private or ip_obj.is_loopback: return
        
        if ip_obj.version == 4:
            ipv4_set.add(str(ip_obj))
        elif ip_obj.version == 6:
            ipv6_set.add(ip_obj.compressed)
    except:
        pass

# --- 多线程工作函数 ---

def resolve_domain_worker(dom):
    """单域名多轮次解析线程"""
    for _ in range(POLL_TIMES):
        try:
            addrs = socket.getaddrinfo(dom, None)
            for a in addrs:
                process_ip(a[4][0])
            time.sleep(0.1) # 略微停顿，防止本地缓存拦截请求
        except:
            break # 解析失败不再死磕

def fetch_source_worker(item):
    """单源深度抓取线程"""
    url, name = item
    ipv4_re = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    ipv6_re = r'([a-fA-F0-9:]{2,39})'
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        raw_content = r.text
        
        # 1. 源码暴力提取
        for ip in re.findall(ipv4_re, raw_content): process_ip(ip)
        for ip in re.findall(ipv6_re, raw_content): process_ip(ip)

        # 2. BeautifulSoup 纯文本提取防遗漏
        if not url.endswith('.txt'):
            soup = BeautifulSoup(raw_content, 'html.parser')
            text_content = soup.get_text(separator=' ') 
            for ip in re.findall(ipv4_re, text_content): process_ip(ip)
            for ip in re.findall(ipv6_re, text_content): process_ip(ip)
        print(f"✅ [成功] 源已抓取: {name}")
    except Exception as e:
        print(f"⚠️ [跳过] 源 {name} (原因: {e})")

# --- 执行逻辑 ---

if __name__ == "__main__":
    start_time = time.time()
    
    unique_domains = list(set(domain_list))
    print(f"🚀 [阶段一] 开启 {MAX_WORKERS_DNS} 线程处理 {len(unique_domains)} 个域名 (各轮询 {POLL_TIMES} 次)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_DNS) as executor:
        # 提交所有域名解析任务
        futures_dns = [executor.submit(resolve_domain_worker, dom) for dom in unique_domains]
        concurrent.futures.wait(futures_dns)

    print(f"\n🚀 [阶段二] 开启 {MAX_WORKERS_HTTP} 线程深度抓取 {len(sources)} 个网页源...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS_HTTP) as executor:
        # 提交所有网页抓取任务
        futures_http = [executor.submit(fetch_source_worker, item) for item in sources.items()]
        concurrent.futures.wait(futures_http)

    # --- 保存文件 ---
    for filename, data_set in [('ipv4.txt', ipv4_set), ('ipv6.txt', ipv6_set)]:
        if os.path.exists(filename): os.remove(filename)
        # 排序写入
        sorted_ips = sorted(list(data_set))
        with open(filename, 'w', encoding='utf-8') as f:
            for ip in sorted_ips:
                f.write(f"{ip}\n")

    end_time = time.time()
    print(f"\n🎉 完美榨干！总耗时: {end_time - start_time:.2f} 秒")
    print(f"📦 斩获 IPv4 数量: {len(ipv4_set)}")
    print(f"📦 斩获 IPv6 数量: {len(ipv6_set)}")
