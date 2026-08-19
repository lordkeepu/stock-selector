import datetime
import re
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# ------------------------------------------------------------------
# 0. 頁面基本設定與自訂 CSS 美化
# ------------------------------------------------------------------
st.set_page_config(
    page_title="台美選股器 (EY版)", page_icon="⚡", layout="wide"
)

st.markdown(
    """
    <style>
    /* 調整主標題樣式 */
    h1 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* 側邊欄邊框微調 */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.2);
    }

    /* 調整資料表格的字型與排版 */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------
# 1. 預設股票母體與中文名稱字典
# ------------------------------------------------------------------
TW_STOCK_LIST = [
    ("2330.TW", "台積電", "半導體/科技"),
    ("2317.TW", "鴻海", "電子零組件/電腦週邊"),
    ("2454.TW", "聯發科", "半導體/科技"),
    ("2308.TW", "台達電", "電子零組件/電腦週邊"),
    ("2881.TW", "富邦金", "金融保險"),
    ("2882.TW", "國泰金", "金融保險"),
    ("2382.TW", "廣達", "電子零組件/電腦週邊"),
    ("2891.TW", "中信金", "金融保險"),
    ("2303.TW", "聯電", "半導體/科技"),
    ("2886.TW", "兆豐金", "金融保險"),
    ("2884.TW", "玉山金", "金融保險"),
    ("1216.TW", "統一", "非必需消費/其他"),
    ("2892.TW", "第一金", "金融保險"),
    ("2880.TW", "華南金", "金融保險"),
    ("2885.TW", "元大金", "金融保險"),
    ("2883.TW", "開發金", "金融保險"),
    ("2002.TW", "中鋼", "航運物流/工業"),
    ("5880.TW", "合庫金", "金融保險"),
    ("2890.TW", "永豐金", "金融保險"),
    ("2357.TW", "華碩", "電子零組件/電腦週邊"),
    ("3008.TW", "大立光", "半導體/科技"),
    ("2412.TW", "中華電", "半導體/科技"),
    ("3034.TW", "聯詠", "半導體/科技"),
    ("2379.TW", "瑞昱", "半導體/科技"),
    ("2301.TW", "光寶科", "電子零組件/電腦週邊"),
    ("2327.TW", "國巨", "電子零組件/電腦週邊"),
    ("2887.TW", "台新金", "金融保險"),
    ("5876.TW", "上海商銀", "金融保險"),
    ("2801.TW", "彰銀", "金融保險"),
    ("3037.TW", "欣興", "電子零組件/電腦週邊"),
    ("2603.TW", "長榮", "航運物流/工業"),
    ("2609.TW", "陽明", "航運物流/工業"),
    ("2615.TW", "萬海", "航運物流/工業"),
    ("2395.TW", "研華", "電子零組件/電腦週邊"),
    ("2408.TW", "南亞科", "半導體/科技"),
    ("1101.TW", "台泥", "航運物流/工業"),
    ("1301.TW", "台塑", "航運物流/工業"),
    ("1303.TW", "南亞", "航運物流/工業"),
    ("1326.TW", "台化", "航運物流/工業"),
    ("6505.TW", "台塑化", "航運物流/工業"),
    ("2912.TW", "統一超", "非必需消費/其他"),
    ("2207.TW", "和泰車", "非必需消費/其他"),
    ("9910.TW", "豐泰", "非必需消費/其他"),
    ("2345.TW", "智邦", "電子零組件/電腦週邊"),
    ("3661.TW", "世芯-KY", "半導體/科技"),
    ("6669.TW", "緯穎", "電子零組件/電腦週邊"),
    ("3231.TW", "緯創", "電子零組件/電腦週邊"),
    ("2356.TW", "英業達", "電子零組件/電腦週邊"),
    ("3711.TW", "日月光投控", "半導體/科技"),
    ("5871.TW", "中租-KY", "金融保險"),
    ("1477.TW", "聚陽", "非必需消費/其他"),
    ("2385.TW", "群光", "電子零組件/電腦週邊"),
    ("9938.TW", "百和", "非必需消費/其他"),
    ("2392.TW", "正崴", "電子零組件/電腦週邊"),
    ("3260.TWO", "威剛", "半導體/科技"),
    ("3324.TWO", "雙鴻", "電子零組件/電腦週邊"),
    ("6274.TWO", "台燿", "電子零組件/電腦週邊"),
    ("3533.TW", "嘉澤", "電子零組件/電腦週邊"),
    ("6121.TWO", "新普", "電子零組件/電腦週邊"),
    ("2352.TW", "佳世達", "電子零組件/電腦週邊"),
    ("2353.TW", "宏碁", "電子零組件/電腦週邊"),
    ("2409.TW", "友達", "半導體/科技"),
    ("3481.TW", "群創", "半導體/科技"),
    ("1802.TW", "台玻", "航運物流/工業"),
    ("2105.TW", "正新", "航運物流/工業"),
    ("2618.TW", "長榮航", "航運物流/工業"),
    ("2610.TW", "華航", "航運物流/工業"),
    ("9904.TW", "寶成", "非必需消費/其他"),
    ("1402.TW", "遠東新", "非必需消費/其他"),
    ("2201.TW", "裕隆", "非必需消費/其他"),
    ("1722.TW", "台肥", "航運物流/工業"),
    ("2204.TW", "中華", "非必需消費/其他"),
    ("2347.TW", "聯強", "電子零組件/電腦週邊"),
    ("2377.TW", "微星", "電子零組件/電腦週邊"),
    ("2383.TW", "台光電", "電子零組件/電腦週邊"),
    ("2404.TW", "漢唐", "半導體/科技"),
    ("2449.TW", "京元電子", "半導體/科技"),
    ("2451.TW", "創見", "半導體/科技"),
    ("3035.TW", "智原", "半導體/科技"),
    ("3044.TW", "健鼎", "電子零組件/電腦週邊"),
    ("3045.TW", "台灣大", "半導體/科技"),
    ("4904.TW", "遠傳", "半導體/科技"),
    ("4938.TW", "和碩", "電子零組件/電腦週邊"),
    ("5483.TWO", "中美晶", "半導體/科技"),
    ("6176.TW", "瑞儀", "半導體/科技"),
    ("6213.TW", "聯茂", "電子零組件/電腦週邊"),
    ("6239.TW", "力成", "半導體/科技"),
    ("6409.TW", "旭隼", "電子零組件/電腦週邊"),
    ("6415.TW", "矽力*-KY", "半導體/科技"),
    ("8046.TW", "南電", "電子零組件/電腦週邊"),
    ("8299.TWO", "群聯", "半導體/科技"),
    ("8454.TW", "富邦媒", "非必需消費/其他"),
    ("9917.TW", "中保科", "非必需消費/其他"),
    ("9921.TW", "巨大", "非必需消費/其他"),
    ("9945.TW", "潤泰新", "非必需消費/其他"),
    ("1102.TW", "亞泥", "航運物流/工業"),
    ("1227.TW", "佳格", "非必需消費/其他"),
    ("1304.TW", "台聚", "航運物流/工業"),
    ("1305.TW", "華夏", "航運物流/工業"),
    ("1314.TW", "中石化", "航運物流/工業"),
    ("1476.TW", "儒鴻", "非必需消費/其他"),
    ("1504.TW", "東元", "航運物流/工業"),
    ("1513.TW", "中興電", "航運物流/工業"),
    ("1519.TW", "華城", "航運物流/工業"),
    ("1560.TW", "中砂", "半導體/科技"),
    ("1707.TW", "葡萄王", "非必需消費/其他"),
    ("1717.TW", "長興", "航運物流/工業"),
    ("1723.TW", "中碳", "航運物流/工業"),
    ("2027.TW", "大成鋼", "航運物流/工業"),
    ("2049.TW", "上銀", "航運物流/工業"),
    ("2103.TW", "台橡", "航運物流/工業"),
    ("2206.TW", "三陽工業", "非必需消費/其他"),
    ("2312.TW", "金寶", "電子零組件/電腦週邊"),
    ("2313.TW", "華通", "電子零組件/電腦週邊"),
    ("2324.TW", "仁寶", "電子零組件/電腦週邊"),
    ("2337.TW", "旺宏", "半導體/科技"),
    ("2344.TW", "華邦電", "半導體/科技"),
    ("2354.TW", "鴻準", "電子零組件/電腦週邊"),
    ("2360.TW", "致茂", "半導體/科技"),
    ("2368.TW", "金像電", "電子零組件/電腦週邊"),
    ("2376.TW", "技嘉", "電子零組件/電腦週邊"),
    ("2388.TW", "威盛", "半導體/科技"),
    ("2401.TW", "凌陽", "半導體/科技"),
    ("2439.TW", "美律", "電子零組件/電腦週邊"),
    ("2458.TW", "義隆", "半導體/科技"),
    ("2474.TW", "可成", "電子零組件/電腦週邊"),
    ("2492.TW", "華新科", "電子零組件/電腦週邊"),
    ("2498.TW", "宏達電", "電子零組件/電腦週邊"),
    ("2501.TW", "國建", "非必需消費/其他"),
    ("2511.TW", "太子", "非必需消費/其他"),
    ("2542.TW", "興富發", "非必需消費/其他"),
    ("2606.TW", "裕民", "航運物流/工業"),
    ("2612.TW", "中航", "航運物流/工業"),
    ("2637.TW", "慧洋-KY", "航運物流/工業"),
    ("2809.TW", "京城銀", "金融保險"),
    ("2812.TW", "台中銀", "金融保險"),
    ("2834.TW", "臺企銀", "金融保險"),
    ("2845.TW", "遠東銀", "金融保險"),
    ("2889.TW", "國票金", "金融保險"),
    ("2903.TW", "遠東百", "非必需消費/其他"),
    ("3036.TW", "文曄", "半導體/科技"),
    ("3042.TW", "晶技", "電子零組件/電腦週邊"),
    ("3189.TW", "景碩", "電子零組件/電腦週邊"),
    ("3406.TW", "玉晶光", "半導體/科技"),
    ("3583.TW", "辛耘", "半導體/科技"),
    ("3702.TW", "大聯大", "半導體/科技"),
    ("3706.TW", "神達", "電子零組件/電腦週邊"),
    ("4958.TW", "臻鼎-KY", "電子零組件/電腦週邊"),
    ("5347.TWO", "世界", "半導體/科技"),
    ("5904.TWO", "寶雅", "非必需消費/其他"),
]

NASDAQ100_LIST = [
    ("AAPL", "Apple", "半導體/科技"),
    ("MSFT", "Microsoft", "半導體/科技"),
    ("NVDA", "NVIDIA", "半導體/科技"),
    ("AMZN", "Amazon", "非必需消費/其他"),
    ("GOOG", "Alphabet C", "半導體/科技"),
    ("GOOGL", "Alphabet A", "半導體/科技"),
    ("META", "Meta", "半導體/科技"),
    ("TSLA", "Tesla", "非必需消費/其他"),
    ("AVGO", "Broadcom", "半導體/科技"),
    ("COST", "Costco", "非必需消費/其他"),
    ("PEP", "PepsiCo", "非必需消費/其他"),
    ("CSCO", "Cisco", "半導體/科技"),
    ("TMUS", "T-Mobile", "半導體/科技"),
    ("ADBE", "Adobe", "半導體/科技"),
    ("AMD", "AMD", "半導體/科技"),
    ("NFLX", "Netflix", "非必需消費/其他"),
    ("TXN", "Texas Instruments", "半導體/科技"),
    ("QCOM", "Qualcomm", "半導體/科技"),
    ("INTC", "Intel", "半導體/科技"),
    ("AMAT", "Applied Materials", "半導體/科技"),
    ("CMCSA", "Comcast", "非必需消費/其他"),
    ("HON", "Honeywell", "航運物流/工業"),
    ("INTU", "Intuit", "半導體/科技"),
    ("BKNG", "Booking Holdings", "非必需消費/其他"),
    ("AMGN", "Amgen", "非必需消費/其他"),
    ("SBUX", "Starbucks", "非必需消費/其他"),
    ("GILD", "Gilead Sciences", "非必需消費/其他"),
    ("MDLZ", "Mondelez", "非必需消費/其他"),
    ("ADI", "Analog Devices", "半導體/科技"),
    ("ADP", "ADP", "半導體/科技"),
    ("LRCX", "Lam Research", "半導體/科技"),
    ("ISRG", "Intuitive Surgical", "非必需消費/其他"),
    ("REGN", "Regeneron", "非必需消費/其他"),
    ("VRTX", "Vertex", "半導體/科技"),
    ("FISV", "Fiserv", "半導體/科技"),
    ("MU", "Micron", "半導體/科技"),
    ("KLAC", "KLA Corporation", "半導體/科技"),
    ("PANW", "Palo Alto Networks", "半導體/科技"),
    ("SNPS", "Synopsys", "半導體/科技"),
    ("CDNS", "Cadence", "半導體/科技"),
    ("MELI", "MercadoLibre", "非必需消費/其他"),
    ("PYPL", "PayPal", "金融保險"),
    ("CSX", "CSX Corporation", "航運物流/工業"),
    ("MAR", "Marriott", "非必需消費/其他"),
    ("ORLY", "O'Reilly Auto Parts", "非必需消費/其他"),
    ("ASML", "ASML Holding", "半導體/科技"),
    ("CTAS", "Cintas", "航運物流/工業"),
    ("NXPI", "NXP Semiconductors", "半導體/科技"),
    ("FTNT", "Fortinet", "半導體/科技"),
    ("MRVL", "Marvell Technology", "半導體/科技"),
    ("ADSK", "Autodesk", "半導體/科技"),
    ("ABNB", "Airbnb", "非必需消費/其他"),
    ("LULU", "Lululemon", "非必需消費/其他"),
    ("MNST", "Monster Beverage", "非必需消費/其他"),
    ("KDP", "Keurig Dr Pepper", "非必需消費/其他"),
    ("ROST", "Ross Stores", "非必需消費/其他"),
    ("WDAY", "Workday", "半導體/科技"),
    ("AEP", "American Electric Power", "航運物流/工業"),
    ("PAYX", "Paychex", "半導體/科技"),
    ("KHC", "Kraft Heinz", "非必需消費/其他"),
    ("ODFL", "Old Dominion Freight", "航運物流/工業"),
    ("IDXX", "Idexx Laboratories", "非必需消費/其他"),
    ("EXC", "Exelon", "航運物流/工業"),
    ("EA", "Electronic Arts", "半導體/科技"),
    ("CTSH", "Cognizant", "半導體/科技"),
    ("MCHP", "Microchip Technology", "半導體/科技"),
    ("CPRT", "Copart", "航運物流/工業"),
    ("XEL", "Xcel Energy", "航運物流/工業"),
    ("FAST", "Fastenal", "航運物流/工業"),
    ("VRSK", "Verisk", "航運物流/工業"),
    ("BKR", "Baker Hughes", "航運物流/工業"),
    ("CSGP", "CoStar Group", "金融保險"),
    ("GEHC", "GE HealthCare", "非必需消費/其他"),
    ("ON", "ON Semiconductor", "半導體/科技"),
    ("ANSS", "Ansys", "半導體/科技"),
    ("BIIB", "Biogen", "非必需消費/其他"),
    ("DLTR", "Dollar Tree", "非必需消費/其他"),
    ("DXCM", "DexCom", "非必需消費/其他"),
    ("WBD", "Warner Bros. Discovery", "非必需消費/其他"),
    ("ILMN", "Illumina", "非必需消費/其他"),
    ("WBA", "Walgreens Boots Alliance", "非必需消費/其他"),
    ("ZS", "Zscaler", "半導體/科技"),
    ("CRWD", "CrowdStrike", "半導體/科技"),
    ("TEAM", "Atlassian", "半導體/科技"),
    ("DDOG", "Datadog", "半導體/科技"),
    ("CEG", "Constellation Energy", "航運物流/工業"),
    ("FANG", "Diamondback Energy", "航運物流/工業"),
    ("TTD", "The Trade Desk", "半導體/科技"),
    ("ARM", "Arm Holdings", "半導體/科技"),
    ("Dash", "DoorDash", "非必需消費/其他"),
    ("MDB", "MongoDB", "半導體/科技"),
    ("ROKU", "Roku", "半導體/科技"),
    ("TTWO", "Take-Two", "半導體/科技"),
    ("GFV", "GlobalFoundries", "半導體/科技"),
    ("SMCI", "Super Micro Computer", "半導體/科技"),
]

SP100_LIST = [
    ("AAPL", "Apple", "半導體/科技"),
    ("MSFT", "Microsoft", "半導體/科技"),
    ("NVDA", "NVIDIA", "半導體/科技"),
    ("AMZN", "Amazon", "非必需消費/其他"),
    ("GOOG", "Alphabet C", "半導體/科技"),
    ("GOOGL", "Alphabet A", "半導體/科技"),
    ("META", "Meta", "半導體/科技"),
    ("TSLA", "Tesla", "非必需消費/其他"),
    ("BRK-B", "Berkshire Hathaway", "金融保險"),
    ("JPM", "JPMorgan Chase", "金融保險"),
    ("LLY", "Eli Lilly", "非必需消費/其他"),
    ("UNH", "UnitedHealth", "非必需消費/其他"),
    ("V", "Visa", "金融保險"),
    ("XOM", "ExxonMobil", "航運物流/工業"),
    ("JNJ", "Johnson & Johnson", "非必需消費/其他"),
    ("WMT", "Walmart", "非必需消費/其他"),
    ("MA", "Mastercard", "金融保險"),
    ("PG", "Procter & Gamble", "非必需消費/其他"),
    ("HD", "Home Depot", "非必需消費/其他"),
    ("AVGO", "Broadcom", "半導體/科技"),
    ("CVX", "Chevron", "航運物流/工業"),
    ("MRK", "Merck", "非必需消費/其他"),
    ("ABBV", "AbbVie", "非必需消費/其他"),
    ("COST", "Costco", "非必需消費/其他"),
    ("ORCL", "Oracle", "半導體/科技"),
    ("KO", "Coca-Cola", "非必需消費/其他"),
    ("BAC", "Bank of America", "金融保險"),
    ("PEP", "PepsiCo", "非必需消費/其他"),
    ("CRM", "Salesforce", "半導體/科技"),
    ("TMO", "Thermo Fisher", "非必需消費/其他"),
    ("CSCO", "Cisco", "半導體/科技"),
    ("MCD", "McDonald's", "非必需消費/其他"),
    ("ACN", "Accenture", "半導體/科技"),
    ("ABT", "Abbott Laboratories", "非必需消費/其他"),
    ("LIN", "Linde", "航運物流/工業"),
    ("NFLX", "Netflix", "非必需消費/其他"),
    ("DHR", "Danaher", "非必需消費/其他"),
    ("AMD", "AMD", "半導體/科技"),
    ("DIS", "Walt Disney", "非必需消費/其他"),
    ("PM", "Philip Morris", "非必需消費/其他"),
    ("TXN", "Texas Instruments", "半導體/科技"),
    ("INTC", "Intel", "半導體/科技"),
    ("WFC", "Wells Fargo", "金融保險"),
    ("VZ", "Verizon", "半導體/科技"),
    ("QCOM", "Qualcomm", "半導體/科技"),
    ("COP", "ConocoPhillips", "航運物流/工業"),
    ("AMGN", "Amgen", "非必需消費/其他"),
    ("IBM", "IBM", "半導體/科技"),
    ("UNP", "Union Pacific", "航運物流/工業"),
    ("LOW", "Lowe's", "非必需消費/其他"),
    ("SPGI", "S&P Global", "金融保險"),
    ("CAT", "Caterpillar", "航運物流/工業"),
    ("GE", "General Electric", "航運物流/工業"),
    ("HON", "Honeywell", "航運物流/工業"),
    ("INTU", "Intuit", "半導體/科技"),
    ("BA", "Boeing", "航運物流/工業"),
    ("RTX", "RTX Corporation", "航運物流/工業"),
    ("AMAT", "Applied Materials", "半導體/科技"),
    ("PFE", "Pfizer", "非必需消費/其他"),
    ("GS", "Goldman Sachs", "金融保險"),
    ("BLK", "BlackRock", "金融保險"),
    ("BKNG", "Booking Holdings", "非必需消費/其他"),
    ("ECL", "Ecolab", "航運物流/工業"),
    ("ISRG", "Intuitive Surgical", "非必需消費/其他"),
    ("MS", "Morgan Stanley", "金融保險"),
    ("NOW", "ServiceNow", "半導體/科技"),
    ("SBUX", "Starbucks", "非必需消費/其他"),
    ("T", "AT&T", "半導體/科技"),
    ("ELV", "Elevance Health", "非必需消費/其他"),
    ("DE", "John Deere", "航運物流/工業"),
    ("UPS", "United Parcel Service", "航運物流/工業"),
    ("PGR", "Progressive", "金融保險"),
    ("LRCX", "Lam Research", "半導體/科技"),
    ("C", "Citigroup", "金融保險"),
    ("GILD", "Gilead Sciences", "非必需消費/其他"),
    ("MDLZ", "Mondelez", "非必需消費/其他"),
    ("LMT", "Lockheed Martin", "航運物流/工業"),
    ("SCHW", "Charles Schwab", "金融保險"),
    ("ADI", "Analog Devices", "半導體/科技"),
    ("TJX", "TJX Companies", "非必需消費/其他"),
    ("ADP", "ADP", "半導體/科技"),
    ("PLD", "Prologis", "金融保險"),
    ("MMC", "Marsh & McLennan", "金融保險"),
    ("CB", "Chubb", "金融保險"),
    ("AMT", "American Tower", "金融保險"),
    ("CI", "Cigna", "非必需消費/其他"),
    ("FI", "Fiserv", "半導體/科技"),
    ("BMY", "Bristol Myers Squibb", "非必需消費/其他"),
    ("MO", "Altria", "非必需消費/其他"),
    ("SO", "Southern Company", "航運物流/工業"),
    ("DUK", "Duke Energy", "航運物流/工業"),
    ("ZTS", "Zoetis", "非必需消費/其他"),
    ("SHW", "Sherwin-Williams", "航運物流/工業"),
    ("REGN", "Regeneron", "非必需消費/其他"),
    ("TGT", "Target", "非必需消費/其他"),
    ("ITW", "Illinois Tool Works", "航運物流/工業"),
    ("CVS", "CVS Health", "非必需消費/其他"),
]

NAME_TO_SYMBOL = {
    "元大台灣50": ("0050.TW", "元大台灣50"),
    "0050": ("0050.TW", "元大台灣50"),
    "元大高股息": ("0056.TW", "元大高股息"),
    "0056": ("0056.TW", "元大高股息"),
    "國泰永續高股息": ("00878.TW", "國泰永續高股息"),
    "00878": ("00878.TW", "國泰永續高股息"),
    "復華台灣科技優息": ("00929.TW", "復華台灣科技優息"),
    "00929": ("00929.TW", "復華台灣科技優息"),
    "富邦日本正二": ("00640L.TW", "富邦日本正二"),
    "00640L": ("00640L.TW", "富邦日本正二"),
    "寶雅": ("5904.TWO", "寶雅"),
    "蘋果": ("AAPL", "Apple"),
    "微軟": ("MSFT", "Microsoft"),
    "輝達": ("NVDA", "NVIDIA"),
    "特斯拉": ("TSLA", "Tesla"),
    "亞馬遜": ("AMZN", "Amazon"),
    "GOOGLE": ("GOOG", "Alphabet C"),
    "GOOGL": ("GOOGL", "Alphabet A"),
    "台積電ADR": ("TSM", "TSMC ADR"),
}

for sym, name, ind in TW_STOCK_LIST + NASDAQ100_LIST + SP100_LIST:
    NAME_TO_SYMBOL[name] = (sym, name)
    short_name = name.replace("-KY", "").replace("*", "")
    if short_name not in NAME_TO_SYMBOL:
        NAME_TO_SYMBOL[short_name] = (sym, name)


# ------------------------------------------------------------------
# 2. 自動爬取最新成分股與快取控制
# ------------------------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_dynamic_universe(universe_key):
    try:
        if universe_key == "nasdaq100":
            url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            df = pd.read_html(url)[4]
            tickers = df["Ticker"].tolist()
            return [(t, t, "美股/科技") for t in tickers]

        elif universe_key == "sp100":
            url = "https://en.wikipedia.org/wiki/S%26P_100"
            df = pd.read_html(url)[2]
            tickers = df["Symbol"].str.replace(".", "-").tolist()
            return [(t, t, "美股/大型") for t in tickers]
    except Exception:
        pass
    return None


# ------------------------------------------------------------------
# 3. 側邊欄與選單控制
# ------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 篩選選項")

    stock_group = st.radio(
        "1. 請選擇核心母體：",
        [
            "台股 - 0050 + 0051",
            "美股 - 納斯達克 100",
            "美股 - S&P 100",
            "⭐ 自選股票清單",
        ],
    )

    st.caption("💡 建議重整時機：每季末 (3/15, 6/15, 9/15, 12/15)")
    if st.button(
        "🔄 重整指數成分股快取",
        help="點擊後將清除快取，下次搜尋時會自動抓取最新的指數成分股名單。",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.success("快取已清除！")

    custom_input_tickers = []
    if stock_group == "⭐ 自選股票清單":
        st.markdown("---")
        user_symbols_text = st.text_area(
            "請輸入股票代號或名稱 (用逗號或換行)：",
            value="台達電,國巨,漢唐,寶雅,goog,富邦日本正二",
        )

        cleaned_text = (
            user_symbols_text.replace("，", ",")
            .replace("。", ",")
            .replace("、", ",")
            .replace(" ", ",")
            .replace("\n", ",")
        )

        cleaned_text = re.sub(
            r"(?<=[\u4e00-\u9fa5a-zA-Z0-9])\.(?=[\u4e00-\u9fa5])",
            ",",
            cleaned_text,
        )

        raw_inputs = [
            item.strip() for item in cleaned_text.split(",") if item.strip()
        ]

        for item in raw_inputs:
            item_upper = item.upper()
            if item in NAME_TO_SYMBOL:
                sym, disp_name = NAME_TO_SYMBOL[item]
                custom_input_tickers.append((sym, disp_name, "自選股票"))
            elif item_upper in NAME_TO_SYMBOL:
                sym, disp_name = NAME_TO_SYMBOL[item_upper]
                custom_input_tickers.append((sym, disp_name, "自選股票"))
            elif item.isdigit():
                custom_input_tickers.append((f"{item}.TW", item, "自選股票"))
            else:
                custom_input_tickers.append(
                    (item_upper, item_upper, "自選股票")
                )

    industry_filter = st.selectbox(
        "2. 細分產業類別：",
        [
            "全部產業 (不限)",
            "半導體/科技",
            "電子零組件/電腦週邊",
            "金融保險",
            "航運物流/工業",
            "非必需消費/其他",
            "自選股票",
        ],
    )

    quadrant_filter = st.selectbox(
        "3. 象限選單：",
        [
            "全部區間",
            "第一象限 (>= 中線*1.05)",
            "第四象限 (<= 中線*0.95)",
            "中線區間 (0.95~1.05之間)",
        ],
    )

    limit_lower_shadow = st.checkbox(
        "📌 限制最新一日為下影線 (含實體與十字下影線)", value=False
    )

    st.markdown("---")
    start_test = st.button(
        "🚀 開始選股", type="primary", use_container_width=True
    )


# ------------------------------------------------------------------
# 4. 主畫面數據處理與繪圖函式
# ------------------------------------------------------------------
st.title("⚡ 台美選股器 (EY版)")


@st.cache_data(ttl=3600)
def fetch_stock_data(symbol):
    try:
        df = yf.download(symbol, period="1y", progress=False)
        if df is None or df.empty or df.dropna(how="all").empty:
            if symbol.endswith(".TW"):
                alt_symbol = symbol.replace(".TW", ".TWO")
                df = yf.download(alt_symbol, period="1y", progress=False)
                if df is not None and not df.empty:
                    return df, alt_symbol
            return None, symbol
        return df, symbol
    except Exception:
        return None, symbol


def generate_tv_symbol(symbol: str) -> str:
    if symbol.endswith(".TW"):
        return f"TWSE:{symbol.replace('.TW', '')}"
    elif symbol.endswith(".TWO"):
        return f"TPEX:{symbol.replace('.TWO', '')}"
    return symbol


def extract_single_value(series_or_df):
    """確保精準取出單一純量浮點數，解決 yfinance MultiIndex 問題"""
    if isinstance(series_or_df, pd.DataFrame):
        val = series_or_df.iloc[:, 0].values[0]
    elif isinstance(series_or_df, pd.Series):
        val = series_or_df.values[0]
    else:
        val = series_or_df
    return float(val)


def check_lower_shadow(latest_row) -> bool:
    high = extract_single_value(latest_row["High"])
    low = extract_single_value(latest_row["Low"])
    open_p = extract_single_value(latest_row["Open"])
    close_p = extract_single_value(latest_row["Close"])

    total_range = high - low
    if total_range == 0:
        return False

    body_bottom = min(open_p, close_p)
    lower_shadow = body_bottom - low
    return (lower_shadow / total_range) >= 0.3


def process_stock(symbol, name, ind, df):
    # 1. 攤平 yfinance MultiIndex 欄位結構
    if isinstance(df.columns, pd.MultiIndex):
        try:
            df = df.xs(symbol, axis=1, level=1, drop_level=True)
        except Exception:
            df.columns = df.columns.get_level_values(0)

    df_clean = df.dropna()
    if len(df_clean) < 5:
        return None

    # 2. 自動以「執行當天 (Today)」為基準，動態回推 365 天
    today = datetime.date.today()
    one_year_ago = today - datetime.timedelta(days=365)

    # 3. 切割近一年 K 線資料 (未滿一年自動採計上市首日起算)
    df_clean_date = df_clean.copy()
    df_target = df_clean_date[df_clean_date.index.date >= one_year_ago]

    if len(df_target) == 0:
        df_target = df_clean

    # 4. 精確提取起點價 (P_past) 與終點價 (P_latest)
    past_close = extract_single_value(df_target["Close"].iloc[0])
    latest_close = extract_single_value(df_target["Close"].iloc[-1])

    # 5. 計算象限歸屬 (標準維持不變：漲幅 >= 10.53% 歸為第一象限；跌幅 >= 9.52% 歸為第四象限)
    price_change_ratio = (latest_close - past_close) / past_close

    if price_change_ratio >= 0.10526:
        quadrant = "第一象限"
    elif price_change_ratio <= -0.09524:
        quadrant = "第四象限"
    else:
        quadrant = "中線區間"

    latest_row = df_target.iloc[-1]
    is_has_lower_shadow = check_lower_shadow(latest_row)
    tv_symbol = generate_tv_symbol(symbol)

    market_type = (
        "台股" if (".TW" in symbol or ".TWO" in symbol) else "美股/ETF"
    )

    return {
        "symbol": symbol,
        "name": name,
        "industry": ind,
        "market": market_type,
        "latest_close": round(latest_close, 2),
        "quadrant": quadrant,
        "is_lower_shadow": is_has_lower_shadow,
        "tv_symbol": tv_symbol,
        "superchart_url": f"https://www.tradingview.com/chart/?symbol={tv_symbol}",
        "df_raw": df_target,
    }


def render_plotly_chart(stock_name: str, df: pd.DataFrame, chart_key: str):
    open_vals = (
        df["Open"].values.flatten()
        if hasattr(df["Open"], "values")
        else df["Open"]
    )
    high_vals = (
        df["High"].values.flatten()
        if hasattr(df["High"], "values")
        else df["High"]
    )
    low_vals = (
        df["Low"].values.flatten() if hasattr(df["Low"], "values") else df["Low"]
    )
    close_vals = (
        df["Close"].values.flatten()
        if hasattr(df["Close"], "values")
        else df["Close"]
    )

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df.index,
                open=open_vals,
                high=high_vals,
                low=low_vals,
                close=close_vals,
                name="K線",
            )
        ]
    )
    fig.update_layout(
        title=f"{stock_name} K線圖",
        xaxis_title="日期",
        yaxis_title="價格",
        xaxis_rangeslider_visible=False,
        height=520,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig, use_container_width=True, key=chart_key)


def sync_table_selection():
    table_state = st.session_state.get("stock_table", {})
    selected_rows = table_state.get("selection", {}).get("rows", [])
    if selected_rows:
        st.session_state["chart_index"] = selected_rows[0]


# ------------------------------------------------------------------
# 5. 執行與左右並排繪製邏輯
# ------------------------------------------------------------------
if start_test or "results" in st.session_state:
    if start_test:
        if stock_group == "台股 - 0050 + 0051":
            target_tuples = TW_STOCK_LIST
        elif stock_group == "美股 - 納斯達克 100":
            dynamic_list = fetch_dynamic_universe("nasdaq100")
            target_tuples = (
                dynamic_list if dynamic_list is not None else NASDAQ100_LIST
            )
        elif stock_group == "美股 - S&P 100":
            dynamic_list = fetch_dynamic_universe("sp100")
            target_tuples = (
                dynamic_list if dynamic_list is not None else SP100_LIST
            )
        else:
            target_tuples = custom_input_tickers

        success_results = []
        progress_bar = st.progress(0, text="正在運算中，請稍候...")

        for idx, (sym, name, ind) in enumerate(target_tuples):
            if (
                industry_filter != "全部產業 (不限)"
                and ind != industry_filter
                and ind != "自選股票"
            ):
                continue

            df_stock, final_symbol = fetch_stock_data(sym)
            if df_stock is None or df_stock.empty:
                continue

            res = process_stock(final_symbol, name, ind, df_stock)
            if res is None:
                continue

            if quadrant_filter != "全部區間":
                target_q = quadrant_filter.split(" ")[0]
                if target_q not in res["quadrant"]:
                    continue

            if limit_lower_shadow and not res["is_lower_shadow"]:
                continue

            success_results.append(res)

            progress_bar.progress(
                (idx + 1) / len(target_tuples),
                text=f"正在分析... ({idx+1}/{len(target_tuples)})",
            )

        progress_bar.empty()
        st.session_state["results"] = success_results
        st.session_state["chart_index"] = 0
        st.session_state["stock_table"] = {
            "selection": {"rows": [0], "columns": []}
        }

    results = st.session_state.get("results", [])
    st.success(f"🎉 分析完成！共篩選出 **{len(results)}** 檔符合條件標的：")

    if results:
        res_df = pd.DataFrame(results)
        display_df = pd.DataFrame({
            "市場": res_df["market"],
            "代號": res_df["symbol"],
            "名稱": res_df["name"],
            "細分產業": res_df["industry"],
            "最新收盤": res_df["latest_close"],
            "歸屬象限": res_df["quadrant"],
            "下影線特徵": res_df["is_lower_shadow"].map(
                {True: "✅ 有", False: "❌ 無"}
            ),
        })

        total_results = len(results)

        if "chart_index" not in st.session_state:
            st.session_state["chart_index"] = 0

        if st.session_state["chart_index"] >= total_results:
            st.session_state["chart_index"] = 0
        if st.session_state["chart_index"] < 0:
            st.session_state["chart_index"] = total_results - 1

        current_idx = st.session_state["chart_index"]

        left_col, right_col = st.columns([1, 1], gap="medium")

        # 左側：互動圖表預覽 & 操作按鈕
        with left_col:
            st.subheader("🔍 互動圖表預覽")

            selected_stock = results[st.session_state["chart_index"]]

            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 1.5])

            with btn_col1:
                if st.button("⬅️ 上一檔", use_container_width=True, key="prev_btn"):
                    new_idx = (current_idx - 1) % total_results
                    st.session_state["chart_index"] = new_idx
                    st.session_state["stock_table"] = {
                        "selection": {"rows": [new_idx], "columns": []}
                    }
                    st.rerun()

            with btn_col2:
                if st.button("下一檔 ➡️", use_container_width=True, key="next_btn"):
                    new_idx = (current_idx + 1) % total_results
                    st.session_state["chart_index"] = new_idx
                    st.session_state["stock_table"] = {
                        "selection": {"rows": [new_idx], "columns": []}
                    }
                    st.rerun()

            with btn_col3:
                st.link_button(
                    "🚀 開啟 TradingView 圖表",
                    selected_stock["superchart_url"],
                    type="primary",
                    use_container_width=True,
                )

            render_plotly_chart(
                f"{selected_stock['symbol']} {selected_stock['name']}",
                selected_stock["df_raw"],
                chart_key=f"chart_{selected_stock['symbol']}_{st.session_state['chart_index']}",
            )

        # 右側：符合條件的選股結果列表
        with right_col:
            st.subheader("📋 符合條件的選股結果列表")
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True,
                height=580,
                on_select=sync_table_selection,
                selection_mode="single-row",
                key="stock_table",
            )

    else:
        st.warning("⚠️ 沒有找到符合篩選條件的股票，請嘗試放寬篩選條件。")

else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "👈 請在左側側邊欄設定好「核心母體」、「產業」與「條件」後，點擊 **🚀 開始選股**"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📊 多維度母體")
        st.write("支援台股 0050/0051、美股標普 100、納斯達克 100 及自選股。")
    with col2:
        st.markdown("### 📈 象限分析")
        st.write("自動計算中線與強弱區間，精準定位潛力標的。")
    with col3:
        st.markdown("### ⚡ 高效互動")
        st.write("結合 Plotly 互動圖表與 TradingView 快速外連。")
