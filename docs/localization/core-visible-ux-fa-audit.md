# ممیزی فارسی‌سازی Core Visible UX

مبنای ممیزی: `develop@069fc9024`

## وضعیت پیش از این فاز

پوشش کلیدهای یکتای `__()` در زمان اجرا (فایل‌های تست حذف شده‌اند):

| بخش | کلید runtime | ترجمه غیرخالی | ناقص | پوشش |
|---|---:|---:|---:|---:|
| Shared shell / Launcher | 5 | 5 | 0 | 100٪ |
| Drive | 90 | 70 | 20 | 77.8٪ |
| Meet | 130 | 72 | 58 | 55.4٪ |
| Slides | 82 | 49 | 33 | 59.8٪ |
| Writer | 139 | 78 | 61 | 56.1٪ |
| Sheets | 257 | 116 | 141 | 45.1٪ |

این اعداد به‌تنهایی بدهی واقعی را کمتر نشان می‌دادند، چون متن‌های زیر هنوز اصلاً وارد `__()` نشده بودند:

- ۱۴۱ مقدار مستقیم `label/title/placeholder/tooltip/description/message` در Drive
- ۴۴ اعلان مستقیم `toast/alert` در Drive، Meet، Slides و Writer
- متن‌های مستقیم فرم ثبت‌نام، جستجو، Share dialog و preview در Drive
- متن‌ها و وضعیت‌های Find/Replace، AI Settings و Version Preview در Sheets
- متن تأیید حذف شرکت‌کننده در Meet

## مشکلات consistency

- برای یک مفهوم چند معادل وجود داشت: `Favourites`، `Favorite`، «مورد دلخواه» و «علاقه‌مندی».
- عبارت‌های عملیاتی نظیر Delete/Remove/Clear در بعضی بخش‌ها بدون توجه به برگشت‌پذیری یکسان ترجمه شده بودند.
- متن‌های E2EE، WebGL، API، CSV/XLSX و نام مدل‌ها یا کاملاً انگلیسی بودند یا معادل فارسی بدون اصطلاح فنی داشتند.
- پیام‌های dynamic در Drive از fragmentهای انگلیسی ساخته می‌شدند و در فارسی ترتیب طبیعی نداشتند.
- تاریخ Version Preview با locale مرورگر و نه زبان فعال Suite نمایش داده می‌شد.

## یافته‌های RTL

تعداد utilityهای فیزیکی در Vueها که باید به‌صورت هدفمند بررسی شوند:

| بخش | تعداد تقریبی |
|---|---:|
| Drive | 71 |
| Meet | 41 |
| Slides | 18 |
| Writer | 54 |
| Sheets | 8 |

بخشی از `left/right`های Slides و Sheets مختص مختصات canvas است و نباید mirror شود. اصلاح RTL باید فقط روی navigation، dialog، popover، toolbar و متن انجام شود.

## برنامه اجرایی

1. **فاز ۱ — پوشش متن visible UX:** استخراج متن‌های مستقیم، تکمیل catalog، یکسان‌سازی اصطلاحات و پیام‌های پویا.
2. **فاز ۲ — RTL هدفمند:** جایگزینی spacing/alignment فیزیکی در shell، sidebar، dialog، popover و toolbar؛ حفظ مختصات editor/canvas.
3. **فاز ۳ — typography و mixed-language:** بررسی Peyda، line-height، overflow، ایزوله‌سازی اصطلاحات فنی و آزمون viewportهای اصلی.

## معیار قابل‌اندازه‌گیری فاز ۱

- همه کلیدهای runtime در Shared shell، Drive، Meet، Slides، Writer و Sheets دارای `msgstr` غیرخالی باشند.
- placeholderهای `{0}` در source و ترجمه دقیقاً یکسان بمانند.
- msgid تکراری در catalog وجود نداشته باشد.
- هیچ مقدار مستقیم قابل‌شناسایی در propertyهای UI و notificationهای این محدوده باقی نماند.
