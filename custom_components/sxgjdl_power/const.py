"""山西地电用电查询 - 常量定义"""

DOMAIN = "sxgjdl_power"
DEFAULT_NAME = "山西地电"

# 配置键
CONF_CONS_NO = "cons_no"
CONF_ORG_NO = "org_no"
CONF_OPEN_ID = "open_id"
CONF_SCAN_INTERVAL = "scan_interval"

# 默认刷新间隔（分钟）
DEFAULT_SCAN_INTERVAL = 60

# API
BASE_URL = "http://ddwxyw.sxgjdl.com/wechart-platform-web"

API_FEES          = "/getFeesByConsNo"          # 电费信息（余额/应收）
API_CONS_INFO     = "/getConsInfoByConsNo"       # 用户基本信息
API_RECORD_LIST   = "/getRecordList"             # 年度每月用电量
API_LIST_BY_YEAR  = "/getListByYear"             # 年度账单明细
API_DAYS_OF_MONTH = "/getDaysOfMonthData"        # 月度每日用电（含预估）
API_DAYS_ONLY     = "/getDaysOnlyData"           # 当日用电（分时）

# 传感器唯一 ID 后缀
SENSOR_BALANCE            = "balance"            # 预付余额
SENSOR_RECEIVABLE         = "receivable_amt"     # 应收电费（待缴）
SENSOR_MONTH_USAGE        = "month_usage"        # 本月用电量 kWh
SENSOR_MONTH_AMT          = "month_amt"          # 本月预估电费
SENSOR_TODAY_USAGE        = "today_usage"        # 今日用电量 kWh
SENSOR_TODAY_AMT          = "today_amt"          # 今日预估电费
SENSOR_YEAR_TOTAL_USAGE   = "year_total_usage"   # 本年累计用电量
SENSOR_YEAR_TOTAL_AMT     = "year_total_amt"     # 本年累计电费
SENSOR_LAST_MONTH_USAGE   = "last_month_usage"   # 上月用电量
SENSOR_LAST_MONTH_AMT     = "last_month_amt"     # 上月电费
SENSOR_UNIT_PRICE         = "unit_price"         # 当前电价 元/kWh
