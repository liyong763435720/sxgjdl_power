# 山西地电用电查询

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/liyong763435720/sxgjdl_power.svg)](https://github.com/liyong763435720/sxgjdl_power/releases)
[![License](https://img.shields.io/github/license/liyong763435720/sxgjdl_power.svg)](LICENSE)

在 Home Assistant 中查询**山西省地方电力（集团）有限公司**的用电数据，支持余额、用电量、电费账单等 15 个传感器，可接入 HA 能源面板。

---

## ✨ 功能

| 传感器 | 说明 | 单位 |
|--------|------|------|
| 预付余额 | 当前预付电费余额 | 元 |
| 应收电费 | 当前待缴金额 | 元 |
| 当前电价 | 每度电价格 | 元/kWh |
| 今日用电量 | 今日消耗电量（次日更新） | kWh |
| 今日预估电费 | 今日估算电费 | 元 |
| 本月用电量 | 本月已结算用电量 | kWh |
| 本月已结电费 | 本月已结算电费 | 元 |
| 本月预估用电量 | 本月预估总用电量 | kWh |
| 本月预估电费 | 本月预估总电费 | 元 |
| 上月用电量 | 上月结算用电量 | kWh |
| 上月电费 | 上月结算电费 | 元 |
| 本年用电量 | 本年累计用电量 | kWh |
| 本年电费 | 本年累计电费 | 元 |
| 最近一期账单电费 | 最新账单应缴金额 | 元 |
| 最近一期账单用电量 | 最新账单用电量 | kWh |

---

## 📦 安装

### 方法一：通过 HACS 安装（推荐）

1. 在 HACS 中点击右上角菜单 → **自定义仓库**
2. 输入仓库地址：`https://github.com/liyong763435720/sxgjdl_power`
3. 类别选择：**集成（Integration）**
4. 点击添加，然后在 HACS 集成列表中找到 **山西地电用电查询** 并安装
5. 重启 Home Assistant

### 方法二：手动安装

1. 下载最新 [Release](https://github.com/liyong763435720/sxgjdl_power/releases) 中的 zip 文件
2. 将 `custom_components/sxgjdl_power` 目录复制到你的 HA 配置目录下的 `custom_components/`
3. 重启 Home Assistant

---

## ⚙️ 配置

安装后，在 **设置 → 设备与服务 → 添加集成** 中搜索 **山西地电**，填写：

| 字段 | 说明 | 如何获取 |
|------|------|----------|
| 户号 (consNo) | 电力用户编号 | 见下方说明 |
| 供电所编号 (orgNo) | 所属供电所编号 | 见下方说明 |
| 微信 openId（可选） | 缴费接口需要，查询可留空 | — |
| 刷新间隔（分钟） | 默认 60 分钟 | — |

### 如何获取户号和供电所编号？

关注微信公众号 **山西地电** → 点击"用电查询" → 进入用电详情页，查看页面 URL：

```
http://ddwxyw.sxgjdl.com/.../dlcx-detail.html?...&consNo=0209605903&orgNo=144160206
```

- `consNo` 的值 = 户号
- `orgNo` 的值 = 供电所编号

---

## 🔋 接入能源面板

在 **设置 → 仪表板 → 能源 → 用电** 中，将 **"本月用电量"** 添加为电网用电传感器，即可在能源面板查看用电趋势。

---

## ❓ 常见问题

**Q: 添加时提示"户号无效"？**  
A: 确认 `consNo` 和 `orgNo` 均正确，两者都在微信用电查询 URL 里。

**Q: 传感器显示"不可用"？**  
A: 检查 HA 能否访问 `http://ddwxyw.sxgjdl.com`（仅 HTTP，无 HTTPS）。

**Q: 今日用电量为 0？**  
A: 服务器次日才上传当日数据，属正常现象。

**Q: 刷新频率多久合适？**  
A: 建议 60 分钟，过于频繁可能被服务器限流。

---

## 📝 许可证

本项目基于 [MIT License](LICENSE) 开源，仅供个人学习和使用。
