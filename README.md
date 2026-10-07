<div align="center">

<img src="src-tauri/icons/128x128.png" width="110" alt="Terencher" />

# 🛠️ Terencher

**سیستم مدیریت ترنچر — اپلیکیشن اندروید**

**Trenching operations management — Android app**

[![Release](https://img.shields.io/github/v/release/hoboho/trencher-manager?style=flat-square&color=4f6bff)](https://github.com/hoboho/trencher-manager/releases/latest)
[![Platform](https://img.shields.io/badge/platform-Android%207%2B-3ddc84?style=flat-square&logo=android&logoColor=white)](#-نصب--install)
[![Rust](https://img.shields.io/badge/core-Rust-000000?style=flat-square&logo=rust&logoColor=white)](#-فناوری--tech-stack)
[![Tauri](https://img.shields.io/badge/shell-Tauri%202-24C8DB?style=flat-square&logo=tauri&logoColor=white)](#-فناوری--tech-stack)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)

</div>

---

## 📥 نصب / Install

<div align="center">

### [⬇️ دانلود آخرین نسخه (APK)](https://github.com/hoboho/trencher-manager/releases/latest)

</div>

```bash
adb install -r terencher-0.1.0-aarch64.apk
```

| | |
| --- | --- |
| Package | `com.terencher.app` |
| ABI | `arm64-v8a` |
| حداقل اندروید | **7.0** (API 24) |
| حجم | ~8.2 MB |

---

## ✨ امکانات / Features

| صفحه | توضیح |
| --- | --- |
| 📊 **داشبورد** | سود خالص، شمارش پروژه/ماشین/اپراتور، پروژه‌های اخیر |
| 🏗️ **پروژه‌ها** | CRUD کامل، نوار پیشرفت مالی، فیلتر وضعیت، جستجو |
| 🚜 **ماشین‌آلات** | CRUD کامل شامل سوخت، نگهداری، عمق/عرض خندق، سرعت، وزن |
| 👷 **اپراتورها** | CRUD کامل شامل دستمزد ساعتی و اضافه‌کاری |
| 💰 **مالی** | دفتر درآمد/هزینه، دسته‌بندی، موجودی، اتصال به پروژه |
| 📈 **گزارش‌ها** | تفکیک وضعیت، هزینه بر اساس دسته، پروژه‌های شاخص، خروجی CSV |
| ⚙️ **تنظیمات** | زبان، پوسته، نسخه، محل ذخیرهٔ داده |

### 🎨 طراحی

- **Glassmorphism** — سطوح شیشه‌ای مات، حاشیهٔ نورانی، سایهٔ نرم
- **پس‌زمینهٔ aurora متحرک** — چهار لکهٔ رنگی با انیمیشن نرم
- **حرکت‌های فنری** — ترنزیشن روی لمس، تب‌ها و فرم‌ها
- **حالت تاریک/روشن** — با تشخیص خودکار تنظیمات سیستم
- **راست‌چین کامل** — چرخش خودکار RTL↔LTR همراه با تغییر زبان

### 🌐 بومی‌سازی

- فارسی و انگلیسی، تغییر در لحظه بدون راه‌اندازی مجدد
- ارقام فارسی، قالب‌بندی پول (هزار/میلیون/میلیارد) و تاریخ
- فونت **وزیرمتن** به‌صورت داخلی (۵ وزن) — کاملاً آفلاین

---

## 🦀 فناوری / Tech Stack

| لایه | فناوری |
| --- | --- |
| هستهٔ منطق و دیتابیس | **Rust** (`terencher-core`) |
| ذخیره‌سازی | **SQLite** (rusqlite, حالت WAL) |
| پوستهٔ اپ | **Tauri 2** (Android) |
| رابط کاربری | ES Modules + CSS خالص |

- هیچ وابستگی فریم‌ورکی در هستهٔ Rust نیست؛ روی هاست قابل تست است
- کاملاً **آفلاین** — بدون هیچ درخواست شبکه‌ای
- داده‌ها در پوشهٔ خصوصی اپ (`app_data_dir/terencher.db`) — بدون نیاز به مجوز حافظه

---

## 🏗️ ساختار پروژه / Project Structure

```
terencher/
├── src/                        # فرانت‌اند (ES Modules، بدون bundler)
│   ├── index.html
│   ├── styles.css              # سیستم طراحی Glassmorphism
│   ├── main.js                 # پوستهٔ اپ: مسیریابی، تب‌بار، FAB، شیت
│   ├── core/
│   │   ├── api.js              # پل Tauri invoke + fallback به localStorage
│   │   ├── form.js             # سازندهٔ فرم اعلانی (bottom sheet)
│   │   ├── format.js           # ارقام فارسی، پول، تاریخ
│   │   ├── i18n.js             # دیکشنری fa/en + مدیریت جهت
│   │   └── ui.js               # ابزارهای DOM، toast، شیت، confirm
│   ├── locales/                # fa.js, en.js
│   ├── screens/                # یک ماژول برای هر صفحه
│   └── assets/fonts/           # وزیرمتن woff2 (آفلاین)
│
├── rust/terencher-core/        # 🦀 هستهٔ دامنه + ذخیره‌سازی (بدون فریم‌ورک)
│   ├── src/models.rs           # ساختارهای Serde
│   ├── src/db.rs               # اسکیما + CRUD تایپ‌دار + تجمیع داشبورد
│   └── tests/db_test.rs        # تست‌های یکپارچه (SQLite در حافظه)
│
├── src-tauri/                  # پوستهٔ Tauri Android
│   └── src/
│       ├── lib.rs              # Builder، پلاگین‌ها، مسیر دیتابیس
│       ├── commands.rs         # #[tauri::command] روی terencher-core
│       └── main.rs
│
├── scripts/build-android.sh    # بیلد کامل و بازتولیدپذیر APK
├── test/smoke.mjs              # تست headless رابط کاربری (jsdom)
└── RELEASE_NOTES.md            # یادداشت‌های انتشار
```

---

## 🧪 تست / Testing

```
Rust core        4 integration tests    ✓
UI (jsdom)      40 assertions           ✓
```

```bash
npm install
npm run test:all      # هر دو مجموعه
npm run test:rust     # فقط هستهٔ Rust
npm run test          # فقط رابط کاربری
```

---

## 🔨 بیلد / Build

نیازمندی‌ها: Node.js ≥ 18، JDK 17، Android SDK (API 34) + NDK 26.1، Rust + Android targets

```bash
# نصب کامل toolchain + بیلد + امضا (کاملاً خودکار)
./scripts/build-android.sh --abi aarch64

# خروجی
#   dist/terencher-0.1.0-aarch64.apk
```

اسکریپت به‌صورت خودکار toolchain را در `.toolchain/` نصب می‌کند (در گیت نیست)،
CA میزبان را در truststore جاوا وارد می‌کند، Rust را برای اندروید کراس‌کامپایل
می‌کند و در پایان APK را با یک کلید خودامضا امضا می‌کند.

دستورات میان‌بر:

```bash
npm run android:init    # تولید پروژهٔ Gradle (یک‌بار)
npm run android:dev     # اجرا روی دستگاه/شبیه‌ساز
npm run android:apk     # بیلد APK
```

---

## 🗺️ نقشهٔ راه / Roadmap

تصمیمات اتخاذشده، شکاف‌های شناسایی‌شده و کارهای آینده در **[`ROADMAP.md`](ROADMAP.md)** ثبت می‌شود.

> مورد فعلی: نبود **کارکرد تراکتور** و **متراژ کار** — طرح مفصل در بخش‌های ۳ تا ۶ آن سند.

---

## 🤝 مشارکت / Contributing

راهنما در [`CONTRIBUTING.md`](CONTRIBUTING.md).

## 📄 مجوز / License

MIT — فایل [`LICENSE`](LICENSE) را ببینید.

---

<div align="center">

**کد اصلی دسکتاپ (PyQt6)** در برچسب [`pyqt-desktop-archive`](https://github.com/hoboho/trencher-manager/tree/pyqt-desktop-archive) بایگانی شده است.

</div>
