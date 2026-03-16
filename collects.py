import requests, re, os, ipaddress, socket
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# ✅ 基础配置
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

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

# 存储结果 (使用 set 自动去重)
ipv4_set = set()
ipv6_set = set()

def process_ip(ip):
    """验证并存储纯 IP"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        # 排除私有地址和回环地址
        if ip_obj.is_private or ip_obj.is_loopback: return
        
        if ip_obj.version == 4:
            ipv4_set.add(str(ip_obj))
        elif ip_obj.version == 6:
            ipv6_set.add(ip_obj.compressed)
    except:
        pass

# --- 执行逻辑 ---

# 1. 解析域名列表
print(f"🔄 正在从 {len(domain_list)} 个域名中解析 IP...")
for dom in list(set(domain_list)):
    try:
        addrs = socket.getaddrinfo(dom, None)
        for a in addrs:
            process_ip(a[4][0])
    except:
        continue

# 2. 爬取 URL 源
ipv4_re = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
ipv6_re = r'([a-fA-F0-9:]{2,39})'

for url, name in sources.items():
    print(f"🌐 正在抓取源: {name}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        content = r.text
        if not url.endswith('.txt'):
            soup = BeautifulSoup(content, 'html.parser')
            content = soup.get_text()
        
        for ip in re.findall(ipv4_re, content): process_ip(ip)
        for ip in re.findall(ipv6_re, content): process_ip(ip)
    except Exception as e:
        print(f"⚠️ 跳过源 {name}")

# --- 保存文件 ---
for filename, data_set in [('ipv4.txt', ipv4_set), ('ipv6.txt', ipv6_set)]:
    if os.path.exists(filename): os.remove(filename)
    # 按自然顺序排序后写入
    sorted_ips = sorted(list(data_set))
    with open(filename, 'w', encoding='utf-8') as f:
        for ip in sorted_ips:
            f.write(f"{ip}\n")

print(f"\n✅ 处理完成！")
print(f"📦 生成的 IPv4 数量: {len(ipv4_set)}")
print(f"📦 生成的 IPv6 数量: {len(ipv6_set)}")
