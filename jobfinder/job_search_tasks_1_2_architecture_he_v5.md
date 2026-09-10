<span dir="rtl">מסמך אפיון וארכיטקטורה  
מערכת חיפוש משרות — משימות 1 ו־2</span>

<span dir="rtl">גרסה מעודכנת: 07.09.2026 \| חלוקה בין פיתוח דטרמיניסטי למודולי AI</span>

# <span dir="rtl">1. מטרת המערכת</span>

<span dir="rtl">להפוך חיפוש עבודה ידני לתהליך יומי שיטתי, מדיד ובר־המשך: משימה 1 מכסה באופן מחזורי מאגר חברות ידוע; משימה 2 מבצעת גילוי רחב ברשת. שתי המשימות חולקות מדיניות, פרופיל מועמדת, מילות חיפוש, היסטוריית הגשות וזיכרון דיווח.</span>

- <span dir="rtl">כיסוי רחב — לא לעצור ב־Top Picks או בתוצאה הראשונה בחברה.</span>

- <span dir="rtl">מניעת כפילויות — אותה משרה ממקורות שונים היא ישות אחת.</span>

- <span dir="rtl">מניעת הגשה חוזרת — הצלבה מחייבת מול היסטוריית ההגשות.</span>

- <span dir="rtl">שקיפות — דיווח מפורש על כיסוי, פערים, כשלים ורמת ודאות.</span>

- <span dir="rtl">רציפות — שמירת state כך שהרצה חוזרת או המשך לא מתחילים מאפס.</span>

# <span dir="rtl">2. מקורות נתונים קנוניים</span>

- <span dir="rtl">/db/tech_companies_master.xlsx — מאגר החברות למשימה 1.</span>

- <span dir="rtl">/db/linkedin_company_directory_final_2026-09-01.xlsx — קשרי LinkedIn מדרגה ראשונה לפי חברה.</span>

- <span dir="rtl">/db/job_applications_master.xlsx — היסטוריית הגשות מחייבת.</span>

- <span dir="rtl">/Anat_Aminof_skills_profile.md — פרופיל הכישורים והניסיון המאומת.</span>

- <span dir="rtl">/job_search_keywords.md — קבוצות מילות חיפוש משותפות.</span>

- <span dir="rtl">/job_discovery_log.md — יומן גילוי ודיווח משותף בין המשימות.</span>

<span dir="rtl">כל הקבצים נקראים מ־ChatGPT Library. Google Drive אינו fallback ואין לבקש חיבור אליו.</span>

# <span dir="rtl">3. כללים משותפים למשימות 1 ו־2</span>

- <span dir="rtl">תחום גיאוגרפי: מרכז ישראל; Hybrid/Onsite. אין Remote מחו״ל.</span>

- <span dir="rtl">יש להשתמש במספר קבוצות מילות חיפוש ובווריאציות קרובות, באנגלית ובעברית.</span>

- <span dir="rtl">יש לשמור כל משרה רלוונטית בחברה — גם כאשר כבר נמצאה משרה חזקה יותר באותה חברה.</span>

- <span dir="rtl">מקור רשמי/ATS עדיף על LinkedIn או לוח דרושים. מקורות ציבוריים משמשים גם לגילוי.</span>

- <span dir="rtl">אין להמציא מיקום, מודל עבודה, Job ID, איש קשר או קישור.</span>

- <span dir="rtl">התאמה נבדקת מול פרופיל הכישורים; כישור שמופיע בפרופיל לא יסומן כפער.</span>

- <span dir="rtl">ה־Application Gate מחייב הצלבה מול job_applications_master.xlsx לפי Job/Requisition ID וגם חברה + וריאציות כותרת. אם לא מכריע — Gmail משמש רק לאימות היסטוריית הגשה.</span>

- <span dir="rtl">משרה שכבר הוגשה: 🔵, תאריך אם ידוע, והטקסט המדויק: „אין פעולה — לא להגיש שוב”.</span>

- <span dir="rtl">role_key: קודם Job/Requisition ID; אחרת חברה + כותרת + מיקום + URL קנוני מנורמלים.</span>

- <span dir="rtl">פרסומים מקבילים מאוחדים. שינוי URL לבדו אינו יוצר משרה חדשה. דיווח חוזר רק בשינוי סטטוס מהותי.</span>

# <span dir="rtl">4. משימה 1 — Tech Companies</span>

<span dir="rtl">מטרה: כיסוי מחזורי ועקבי של מאגר חברות הטכנולוגיה הידוע, ללא תלות במנועי חיפוש.</span>

- <span dir="rtl">בכל ריצה קוראים בזמן אמת את Master Companies.</span>

- <span dir="rtl">חלוקה דינמית למקטעים עוקבים של עד 150 חברות; אין מספר כולל קשיח.</span>

- <span dir="rtl">בתחילת הריצה מקפיאים את טווח השורות ורשימת החברות של אותו יום.</span>

- <span dir="rtl">לאחר המקטע האחרון חוזרים לתחילת הרשימה; חברה חדשה נכנסת אוטומטית למחזור.</span>

- <span dir="rtl">לכל חברה: איתור אתר הקריירה/ATS, חיפוש משפחות התפקידים, מעבר על Pagination/Load More/מסננים, ושמירת כל המשרות הרלוונטיות.</span>

- <span dir="rtl">סטטוס חברה נשמר: הושלם / אין משרות רלוונטיות / לא נגיש / חלקי.</span>

- <span dir="rtl">מדדי כיסוי: טווח חברות, expected מול processed, סטטוס לכל חברה ומספר דפי משרות שנבדקו.</span>

<span dir="rtl">משפחות תפקידים עיקריות: Project Manager, Technical/Software/R&D Project Manager, Program Manager, Technical/R&D Program Manager, TPM, Release Manager, Project & Release Manager, Delivery Manager ו־Technical Delivery Manager בעלי אופי טכנולוגי. מוחרגים Frontend כללי ו־Delivery לא־טכנולוגי.</span>

# <span dir="rtl">5. משימה 2 — Open Web / Google-Web Intent</span>

<span dir="rtl">מטרה: גילוי רחב של משרות וחברות חדשות שאינן תלויות ברשימת החברות הקיימת.</span>

- <span dir="rtl">חיפוש במטריצה: משפחת תפקיד × משפחת מקור.</span>

- <span dir="rtl">מקורות: Web/Google, LinkedIn ציבורי, Indeed, Glassdoor, לוחות ישראליים שעולים בחיפוש, אתרי חברות ו־ATS כגון Greenhouse, Lever, Workday ו־Comeet.</span>

- <span dir="rtl">משפחות תפקידים כוללות Project/Program/TPM/Release/Delivery, Product Operations, Engineering/R&D Operations ו־Technical Product Manager בהתאם לכללי הסינון.</span>

- <span dir="rtl">שאילתות באנגלית ובעברית, וריאציות יחיד/רבים וכותרות חלופיות, עם Israel / Tel Aviv / Center / Gush Dan / Hybrid / Onsite לפי הצורך.</span>

- <span dir="rtl">מעבר על Pagination/הרחבות עד מיצוי מרחב החיפוש היומי.</span>

- <span dir="rtl">כאשר מתגלה חברה, בודקים את כל המשרות הרלוונטיות שלה ולא רק את המודעה שהובילה אליה.</span>

- <span dir="rtl">Checklist לכל תא תפקיד × מקור; תא שלא הושלם מתועד כפער כיסוי.</span>

- <span dir="rtl">מדדי כיסוי: מקורות שנוסו, תאים שהושלמו, הרחבות/עמודים, חברות ומודעות שנבדקו.</span>

# <span dir="rtl">6. שינוי חשוב: Discovery יומי מול Deep Verification</span>

<span dir="rtl">הגרסה הנוכחית מפרידה בין הריצה היומית האוטומטית לבין אימות עמוק שמבוצע בהמשך לפי בקשה. זה מחליף את הגרסה הישנה שבה כל משרה הייתה חייבת לעבור עד טופס Apply חי בתוך הריצה היומית.</span>

- <span dir="rtl">הריצה היומית: discovery + screening בסיסי + deduplication + Application Gate. משרה חדשה שלא הוגשה מסומנת ⚪ „מועמד לבדיקה”.</span>

- <span dir="rtl">הריצה היומית אינה חייבת לעבור את כל Careers/ATS, לפתוח Apply, לוודא טופס חי, לחקור קשרי LinkedIn או לבצע retries עמוקים.</span>

- <span dir="rtl">Deep Verification לפי בקשה: אימות מודעה רשמית, סטטוס פתוח, Apply path, טופס הגשה, התאמה מלאה, קשרים וסטטוס פעולה.</span>

- <span dir="rtl">🔵 נשאר מחייב גם בריצה היומית כאשר הוכח שכבר הוגשה המשרה.</span>

# <span dir="rtl">7. Retry, Coverage ו־Continuation</span>

- <span dir="rtl">State נשמר לכל חברה/מקור/תא/עמוד כך שכשל חלקי אינו מוחק התקדמות.</span>

- <span dir="rtl">Retry ממוקד מופעל רק על החלק החסר; אין צורך להריץ מחדש רכיבים שכבר הושלמו.</span>

- <span dir="rtl">בשלב אימות עמוק ניתן לבצע עד 5 ניסיונות ממוקדים לרכיב חסר, עם שינוי שאילתה/נתיב/מקור.</span>

- <span dir="rtl">אם נשאר פער: „כיסוי חלקי — נדרשת ריצת המשך” + פירוט מדויק של החסר.</span>

- <span dir="rtl">ריצת המשך מציגה רק משרות חדשות או שינויי סטטוס; אם אין חדשות: „לא נמצאו משרות חדשות נוספות בריצת ההמשך”.</span>

# <span dir="rtl">8. פורמט הדוח</span>

<span dir="rtl">כותרת: 📅 חיפוש משרות — DD.MM.YYYY. יש לציין שם ריצה, זמן, ומצב כיסוי.</span>

<span dir="rtl">בריצה היומית, עבור ⚪: חברה, תפקיד, קישור מקור הגילוי, מיקום/מודל עבודה אם ידוע, התאמה/פערים ראשוניים ותוצאת Application Gate.</span>

<span dir="rtl">ב־Deep Verification סדר השדות:</span>

- <span dir="rtl">עיגול סטטוס יחיד בכותרת</span>

- <span dir="rtl">מיקום \| מודל עבודה</span>

- <span dir="rtl">Requisition/Job ID אם קיים</span>

- <span dir="rtl">אחוז התאמה</span>

- <span dir="rtl">למה מתאים</span>

- <span dir="rtl">פערים</span>

- <span dir="rtl">הגשה קודמת</span>

- <span dir="rtl">כל קשרי LinkedIn מדרגה ראשונה שנמצאו</span>

- <span dir="rtl">סטטוס מילולי</span>

- <span dir="rtl">המלצה</span>

- <span dir="rtl">קישור רשמי ישיר להגשה</span>

<span dir="rtl">מקרא: 🟢 להגשה · 🟡 דורשת אימות · 🔵 כבר הוגש · 🔴 לא להגשה. ⚪ = מועמד חדש לבדיקה בריצת discovery.</span>

# <span dir="rtl">9. ארכיטקטורה מוצעת — מה קוד ומה AI</span>

| <span dir="rtl">רכיב</span>                       | <span dir="rtl">אחריות</span>                                          | <span dir="rtl">מימוש</span>    | <span dir="rtl">למה</span>                                                       |
|---------------------------------------------------|------------------------------------------------------------------------|---------------------------------|----------------------------------------------------------------------------------|
| <span dir="rtl">Scheduler / Orchestrator</span>   | <span dir="rtl">הפעלת משימות, checkpoints, continuation</span>         | <span dir="rtl">קוד</span>      | <span dir="rtl">דטרמיניסטי, ניתן לבדיקה ולשחזור</span>                           |
| <span dir="rtl">Config & Policy Loader</span>     | <span dir="rtl">טעינת policy, keywords, skills, DB files</span>        | <span dir="rtl">קוד</span>      | <span dir="rtl">I/O ו־validation</span>                                          |
| <span dir="rtl">Company Batch Manager</span>      | <span dir="rtl">בחירת עד 150 חברות והתקדמות במחזור</span>              | <span dir="rtl">קוד</span>      | <span dir="rtl">אלגוריתם פשוט ודטרמיניסטי</span>                                 |
| <span dir="rtl">Search Query Builder</span>       | <span dir="rtl">יצירת שאילתות בסיס מתוך keyword groups</span>          | <span dir="rtl">קוד + AI</span> | <span dir="rtl">קוד מייצר קומבינציות; AI מוסיף וריאציות סמנטיות לא צפויות</span> |
| <span dir="rtl">Web/ATS Fetcher</span>            | <span dir="rtl">HTTP/API/browser, pagination, rate limits</span>       | <span dir="rtl">קוד</span>      | <span dir="rtl">גישה לרשת אינה דורשת AI כשמבנה המקור ידוע</span>                 |
| <span dir="rtl">Page Understanding</span>         | <span dir="rtl">זיהוי משרות מתוך דפים שונים ודינמיים</span>            | <span dir="rtl">AI + קוד</span> | <span dir="rtl">AI מבין מבנה/טקסט משתנה; קוד שומר ומוודא שדות</span>             |
| <span dir="rtl">Role Relevance Classifier</span>  | <span dir="rtl">האם התפקיד בתחום המבוקש/Delivery טכנולוגי</span>       | <span dir="rtl">AI</span>       | <span dir="rtl">החלטה סמנטית שאינה מסתכמת במילת מפתח</span>                      |
| <span dir="rtl">Normalization</span>              | <span dir="rtl">נרמול חברה, title, location, URL, IDs</span>           | <span dir="rtl">קוד</span>      | <span dir="rtl">כללים יציבים</span>                                              |
| <span dir="rtl">Dedup Engine</span>               | <span dir="rtl">role_key, איחוד mirrors, שינויי סטטוס</span>           | <span dir="rtl">קוד</span>      | <span dir="rtl">צריך עקביות ו־idempotency</span>                                 |
| <span dir="rtl">Application Gate</span>           | <span dir="rtl">חיפוש ב־xlsx; fallback Gmail במקרה לא מכריע</span>     | <span dir="rtl">קוד + AI</span> | <span dir="rtl">קוד למאצ'ים חזקים; AI לפירוש וריאציות/מיילים עמומים</span>       |
| <span dir="rtl">Fit & Gap Analysis</span>         | <span dir="rtl">השוואת דרישות המשרה לפרופיל</span>                     | <span dir="rtl">AI</span>       | <span dir="rtl">דורש הבנת משמעות והקשר</span>                                    |
| <span dir="rtl">Official-source Resolution</span> | <span dir="rtl">בחירת מודעה רשמית מול mirror</span>                    | <span dir="rtl">קוד + AI</span> | <span dir="rtl">כללי domain/ID בקוד; AI כשיש עמימות</span>                       |
| <span dir="rtl">Coverage Checklist</span>         | <span dir="rtl">expected/processed, matrix cells, missing paths</span> | <span dir="rtl">קוד</span>      | <span dir="rtl">מדידה דטרמיניסטית</span>                                         |
| <span dir="rtl">Retry Manager</span>              | <span dir="rtl">ניסיון חוזר רק לחלק החסר</span>                        | <span dir="rtl">קוד</span>      | <span dir="rtl">state machine</span>                                             |
| <span dir="rtl">Report Generator</span>           | <span dir="rtl">מבנה, צבעים, ספירות, קישורים</span>                    | <span dir="rtl">קוד + AI</span> | <span dir="rtl">קוד לפורמט; AI לנימוק התאמה/פערים</span>                         |
| <span dir="rtl">Discovery Ledger</span>           | <span dir="rtl">שמירת first_found, verified, task, status</span>       | <span dir="rtl">קוד</span>      | <span dir="rtl">Persistence עקבי</span>                                          |

# <span dir="rtl">10. גבול ברור למודול ה־AI</span>

<span dir="rtl">ה־AI אינו מנהל את ה־state ואינו מחליט אם הריצה „הושלמה” על סמך תחושה. הוא מקבל יחידות עבודה מוגדרות ומחזיר פלט מובנה.</span>

- <span dir="rtl">AI Query Expansion — קלט: משפחת תפקיד + מילות חיפוש; פלט: וריאציות סמנטיות.</span>

- <span dir="rtl">AI Job Extractor/Interpreter — קלט: טקסט/DOM של עמוד; פלט: title, company, location, ID, requirements, evidence.</span>

- <span dir="rtl">AI Relevance & Fit — קלט: משרה + skills profile; פלט: relevant?, fit score, reasons, real gaps.</span>

- <span dir="rtl">AI Ambiguity Resolver — מופעל רק כשכללים דטרמיניסטיים לא מכריעים: title aliases, טכנולוגי מול לא־טכנולוגי, התאמת מייל הגשה למשרה.</span>

<span dir="rtl">כל פלט AI צריך להיות JSON/Schema מובנה עם evidence/confidence. הקוד הוא זה שמבצע validation, dedup, persistence, retries, coverage והפקת סטטוס סופי.</span>

# <span dir="rtl">11. זרימת מערכת מומלצת</span>

<span dir="rtl">Scheduler → Load Canonical Data → Build Work Units → Search/Fetch → AI Extract/Interpret → Deterministic Normalize & Dedup → Application Gate → AI Relevance/Fit → Persist Ledger & Coverage → Generate Report → Continuation Queue.</span>

<span dir="rtl">ב־Deep Verification מתווסף: Official Job → Apply Path → Live Form Check → Contacts → Final actionable status.</span>

# <span dir="rtl">12. עקרונות בדיקות</span>

- <span dir="rtl">Unit tests: normalization, role_key, batch rotation, dedup, status transitions, coverage math.</span>

- <span dir="rtl">Contract tests: schema של תשובות AI; שדות חסרים/לא חוקיים נדחים.</span>

- <span dir="rtl">Fixture tests: דפי Careers/ATS שמורים מסוגים שונים.</span>

- <span dir="rtl">Regression: אותה משרה בשני מקורות; כמה משרות באותה חברה; חברה חדשה; URL שהשתנה; משרה שכבר הוגשה; כשל באמצע והמשך.</span>

- <span dir="rtl">Smoke test יומי: קבצי המקור נגישים, batch נבחר, לפחות מקור חיפוש אחד עובד, ledger ניתן לקריאה/כתיבה.</span>

# <span dir="rtl">13. מסקנת תכנון</span>

<span dir="rtl">רוב המערכת יכולה וצריכה להיות קוד רגיל: orchestration, קבצים, state, pagination, dedup, retries, coverage, persistence ודוחות. ה־AI ממוקם רק בנקודות שבהן נדרשת הבנת שפה והקשר: הרחבת חיפוש, פירוש עמודים לא אחידים, סיווג רלוונטיות, התאמה ופתרון עמימות. כך מתקבלת מערכת יציבה ובדיקה, בלי להפוך כל שלב לקריאת AI יקרה ולא דטרמיניסטית.</span>

<span dir="rtl">נספח א׳ — ארכיטקטורת Client–Server וסטאק טכנולוגי חינמי</span>

<span dir="rtl">מטרת הנספח</span>

<span dir="rtl">להגדיר את ארכיטקטורת היישום בפועל: React + TypeScript בצד הלקוח, FastAPI/Python בצד השרת, והפרדה ברורה בין UI, מנוע החיפוש, שכבת הנתונים ומודולי ה-AI. התכנון מבוסס על רכיבים חינמיים וקוד פתוח, ויכול לרוץ מקומית ללא עלות תשתית קבועה.</span>

<span dir="rtl">א.1 תרשים ארכיטקטורה</span>

<span dir="rtl">React + TypeScript + Vite</span>

<span dir="rtl">↓ REST API / JSON</span>

<span dir="rtl">FastAPI / Python</span>

<span dir="rtl">↓</span>

<span dir="rtl">Orchestrator / Search Engine / Application Gate / Dedup / Coverage / Reports</span>

<span dir="rtl">↓ ↓ ↓</span>

<span dir="rtl">Playwright/HTTP SQLite/Excel AI Provider</span>

<span dir="rtl">↓</span>

<span dir="rtl">Ollama + Local LLM</span>

<span dir="rtl">א.2 חלוקת אחריות בין Client ל-Server</span>

| <span dir="rtl">שכבה</span>            | <span dir="rtl">טכנולוגיה</span>                                        | <span dir="rtl">אחריות</span>                                                                                                      |
|----------------------------------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| <span dir="rtl">Client / UI</span>     | <span dir="rtl">React + TypeScript + Vite</span>                        | <span dir="rtl">מסכי ריצות, משרות, חברות, סינון, סטטוסים, progress, Deep Verification ופתיחת קישורים.</span>                       |
| <span dir="rtl">API Server</span>      | <span dir="rtl">FastAPI + Python</span>                                 | <span dir="rtl">נקודת הכניסה היחידה של ה-UI לשרת. Validation, endpoints, errors ו-DTOs.</span>                                     |
| <span dir="rtl">Orchestrator</span>    | <span dir="rtl">Python</span>                                           | <span dir="rtl">ניהול Task 1/2, יצירת work units, תזמון, retries, continuation וסטטוס ריצה.</span>                                 |
| <span dir="rtl">Search / Fetch</span>  | <span dir="rtl">Playwright + httpx + BeautifulSoup/lxml</span>          | <span dir="rtl">גלישה, pagination, Load More, ATS, Careers pages ו-HTML parsing.</span>                                            |
| <span dir="rtl">State / DB</span>      | <span dir="rtl">SQLite</span>                                           | <span dir="rtl">runs, jobs, companies, ledger, coverage, dedup keys וסטטוסים.</span>                                               |
| <span dir="rtl">Canonical Excel</span> | <span dir="rtl">openpyxl / pandas</span>                                | <span dir="rtl">קריאה/כתיבה של job_applications_master.xlsx ושאר קבצי המקור הקנוניים.</span>                                       |
| <span dir="rtl">AI Service</span>      | <span dir="rtl">AIProvider: Ollama כברירת מחדל; OpenAI API בעתיד</span> | <span dir="rtl">ממשק אחיד ל-Query expansion, הבנת מודעות, relevance/fit ופתרון עמימות. כל provider מחזיר אותו schema מובנה.</span> |
| <span dir="rtl">Scheduler</span>       | <span dir="rtl">APScheduler / cron / Windows Task Scheduler</span>      | <span dir="rtl">הרצות יומיות אוטומטיות ללא תלות ב-UI.</span>                                                                       |
| <span dir="rtl">Tests</span>           | <span dir="rtl">pytest</span>                                           | <span dir="rtl">Unit, contract, regression, fixtures ו-smoke tests.</span>                                                         |

<span dir="rtl">א.3 עיקרון תכנון מרכזי</span>

- <span dir="rtl">צד ה-React אינו פונה ישירות לאתרי דרושים, לקבצי Excel או למודל AI. הוא פונה רק ל-FastAPI.</span>

- <span dir="rtl">השרת הוא בעל ה-state והאחריות העסקית: deduplication, Application Gate, coverage, retries, persistence וסטטוס סופי.</span>

- <span dir="rtl">ה-AI הוא שירות פנימי של השרת ולא מקור אמת. הוא מחזיר JSON מובנה; Python מאמת ומחליט כיצד להשתמש בו.</span>

- <span dir="rtl">הרצות מתוזמנות ממשיכות לעבוד גם כשהדפדפן סגור וה-UI אינו פתוח.</span>

<span dir="rtl">א.4 API מוצע</span>

| <span dir="rtl">Endpoint</span>                            | <span dir="rtl">מטרה</span>                                       |
|------------------------------------------------------------|-------------------------------------------------------------------|
| <span dir="rtl">POST /api/runs/task1</span>                | <span dir="rtl">התחלת ריצת Task 1.</span>                         |
| <span dir="rtl">POST /api/runs/task2</span>                | <span dir="rtl">התחלת ריצת Task 2.</span>                         |
| <span dir="rtl">GET /api/runs/{run_id}</span>              | <span dir="rtl">סטטוס, progress ו-coverage של ריצה.</span>        |
| <span dir="rtl">GET /api/jobs</span>                       | <span dir="rtl">שליפת משרות עם filters, pagination ו-sort.</span> |
| <span dir="rtl">GET /api/jobs/{job_id}</span>              | <span dir="rtl">פרטי משרה מלאים.</span>                           |
| <span dir="rtl">POST /api/jobs/{job_id}/deep-verify</span> | <span dir="rtl">הפעלת Deep Verification למשרה מסוימת.</span>      |
| <span dir="rtl">GET /api/companies</span>                  | <span dir="rtl">רשימת חברות ומצב הכיסוי/הרוטציה.</span>           |
| <span dir="rtl">GET /api/dashboard</span>                  | <span dir="rtl">סיכום ריצה אחרונה, סטטוסים ומדדים.</span>         |

<span dir="rtl">א.5 UI מוצע</span>

<span dir="rtl">• Dashboard — ריצה אחרונה, coverage, מספר משרות חדשות, Applied, Partial ו-errors.</span>

<span dir="rtl">• Runs — היסטוריית Task 1/2 עם progress ויכולת לפתוח run בודד.</span>

<span dir="rtl">• Jobs — טבלה/כרטיסים עם status, fit, company, title, location, source, applied date וקישור.</span>

<span dir="rtl">• Job Details — reasons, gaps, evidence, source resolution ו-Deep Verification.</span>

<span dir="rtl">• Companies — Task 1 rotation, batch נוכחי, last scanned ו-company coverage.</span>

<span dir="rtl">• Configuration — מסך מצומצם ב-V1 לעריכת Companies, Search Keywords, Role Families ו-Search Sources. שינויים נשמרים דרך השרת ב-DB/config; אין לוגיקה עסקית ב-React.</span>

<span dir="rtl">א.6 ספריות Frontend מומלצות — כולן חינמיות</span>

| <span dir="rtl">צורך</span>                       | <span dir="rtl">בחירה</span>                            |
|---------------------------------------------------|---------------------------------------------------------|
| <span dir="rtl">UI framework</span>               | <span dir="rtl">React</span>                            |
| <span dir="rtl">Language</span>                   | <span dir="rtl">TypeScript</span>                       |
| <span dir="rtl">Build tool</span>                 | <span dir="rtl">Vite</span>                             |
| <span dir="rtl">Component library</span>          | <span dir="rtl">MUI או shadcn/ui</span>                 |
| <span dir="rtl">Server-state / API cache</span>   | <span dir="rtl">TanStack Query</span>                   |
| <span dir="rtl">Routing</span>                    | <span dir="rtl">React Router</span>                     |
| <span dir="rtl">Forms</span>                      | <span dir="rtl">React Hook Form</span>                  |
| <span dir="rtl">Validation shared concepts</span> | <span dir="rtl">Zod בצד הלקוח; Pydantic בצד השרת</span> |

<span dir="rtl">א.7 מודל AI חינמי</span>

<span dir="rtl">ברירת המחדל תהיה Ollama עם מודל מקומי מתאים (למשל משפחת Qwen/Llama/Mistral לפי ביצועי המחשב). שכבת AIProvider תהיה interface נפרד, כדי שניתן יהיה בעתיד להחליף למודל ענן בלי לשנות את ה-Orchestrator או ה-UI.</span>

<span dir="rtl">א.8 פריסה חינמית — שלב ראשון</span>

<span dir="rtl">המערכת כולה יכולה לרוץ מקומית על מחשב אחד: React נבנה סטטית ומוגש מקומית, FastAPI רץ כ-service מקומי, SQLite וקבצי Excel נשמרים בדיסק, Ollama רץ מקומית, וה-Scheduler מפעיל את המשימות. במבנה זה אין צורך בשרת ענן, database מנוהל או API בתשלום.</span>

<span dir="rtl">א.9 החלטת ארכיטקטורה</span>

<span dir="rtl">הבחירה הרשמית לפרויקט: Client–Server. Frontend ב-React + TypeScript; Backend ב-FastAPI/Python; SQLite בשלב הראשון; Playwright/httpx למנוע האיסוף; Ollama ל-AI מקומי; וכל הלוגיקה הדטרמיניסטית נשארת בשרת. Streamlit אינו חלק מארכיטקטורת היעד.</span>

<span dir="rtl">א.10 היקף ארכיטקטוני מחייב ל-V1</span>

<span dir="rtl">ב-V1 נשקיע בגבולות ארכיטקטוניים שקשה ויקר לשנות בדיעבד. לעומת זאת, יכולות שאפשר להוסיף בעתיד ללא refactor משמעותי נדחות בכוונה. העיקרון: גמישות רק במקום שבו כבר ידוע שיש סבירות גבוהה לשינוי.</span>

| <span dir="rtl">נושא</span>                          | <span dir="rtl">V1</span>               | <span dir="rtl">מימוש ב-V1</span>                                                                               | <span dir="rtl">למה עכשיו</span>                                           |
|------------------------------------------------------|-----------------------------------------|-----------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|
| <span dir="rtl">הפרדת Client–Server</span>           | <span dir="rtl">חובה</span>             | <span dir="rtl">React מציג ופונה ל-API בלבד; לוגיקה עסקית, scraping, state ו-AI נשארים בשרת.</span>             | <span dir="rtl">מונע זליגת לוגיקה ל-UI ו-refactor גדול בעתיד.</span>       |
| <span dir="rtl">מודל נתונים מרכזי</span>             | <span dir="rtl">חובה</span>             | <span dir="rtl">Job, Run, ApplicationStatus, Coverage ו-JobAnalysis מוגדרים פעם אחת בשרת וממופים ל-DTOs.</span> | <span dir="rtl">מונע מבנים שונים בין Task 1, Task 2 וה-UI.</span>          |
| <span dir="rtl">API contracts מסודרים</span>         | <span dir="rtl">חובה</span>             | <span dir="rtl">FastAPI + Pydantic עם schemas יציבים ו-versionable.</span>                                      | <span dir="rtl">מקטין שבירות בין frontend ל-backend.</span>                |
| <span dir="rtl">AIProvider מתחלף</span>              | <span dir="rtl">חובה</span>             | <span dir="rtl">ממשק אחיד; V1 עם Ollama. OpenAIProvider יכול להתווסף ללא שינוי ב-Tasks או ב-UI.</span>          | <span dir="rtl">מונע תלות בספק AI מסוים.</span>                            |
| <span dir="rtl">Schema אחיד לתשובת AI</span>         | <span dir="rtl">חובה</span>             | <span dir="rtl">כל provider מחזיר JobAnalysis מובנה עם evidence/confidence.</span>                              | <span dir="rtl">מונע parsing שונה בכל מקום.</span>                         |
| <span dir="rtl">Dedup כמודול עצמאי</span>            | <span dir="rtl">חובה</span>             | <span dir="rtl">שירות משותף ל-Task 1 ול-Task 2 עם role_key ואיחוד mirrors.</span>                               | <span dir="rtl">מונע שכפול לוגיקה וסטטוסים סותרים.</span>                  |
| <span dir="rtl">Application Gate כמודול עצמאי</span> | <span dir="rtl">חובה</span>             | <span dir="rtl">בדיקה משותפת מול היסטוריית הגשות, עם fallback לאימות במקרה עמום.</span>                         | <span dir="rtl">מונע לוגיקת הגשות שונה בין המשימות.</span>                 |
| <span dir="rtl">ATS adapters</span>                  | <span dir="rtl">כן, במידה פרקטית</span> | <span dir="rtl">Adapters ל-Greenhouse, Lever, Comeet, Workday ו-Generic Careers כאשר בפועל יש הבדל טכני.</span> | <span dir="rtl">מונע תנאי if מפוזרים, בלי לבנות framework גנרי מדי.</span> |
| <span dir="rtl">Config חיצוני לדברים משתנים</span>   | <span dir="rtl">כן</span>               | <span dir="rtl">Role families, keywords, batch size, search sources, retry settings, AI provider/model.</span>  | <span dir="rtl">מאפשר שינוי שוטף בלי לגעת בקוד.</span>                     |
| <span dir="rtl">Prompts חיצוניים</span>              | <span dir="rtl">כן</span>               | <span dir="rtl">קבצי prompt נפרדים ל-relevance, fit, extraction ו-query expansion.</span>                       | <span dir="rtl">מאפשר לשפר התנהגות AI בלי refactor.</span>                 |

<span dir="rtl">א.11 מה נדחה בכוונה אחרי V1</span>

<span dir="rtl">הפריטים הבאים אינם תנאי לארכיטקטורה טובה של V1. אין צורך לבנות אותם מראש, משום שאפשר להוסיף אותם בעתיד בעלות סבירה אם וכאשר יהיה צורך:</span>

- <span dir="rtl">PostgreSQL abstraction מלאה — V1 משתמש ב-SQLite. יש לשמור גישה מרוכזת לנתונים, אך אין צורך לבנות שכבת ORM/Repository גנרית רק לצורך מעבר עתידי.</span>

- <span dir="rtl">Authentication, משתמשים והרשאות — נדחה כל עוד המערכת מיועדת למשתמשת אחת.</span>

- <span dir="rtl">Settings UI מלא — נדחה. ב-V1 כן קיים מסך Configuration מצומצם עבור נתונים עסקיים שהמשתמשת צפויה לשנות בעצמה: חברות, מילות חיפוש, Role Families ומקורות חיפוש. אין צורך לחשוף ב-UI כל פרמטר פנימי של המערכת.</span>

- <span dir="rtl">Report Provider / Export framework — נבנה פורמט דוח אחד טוב; PDF/Excel/Email exporters נוספים רק אם יידרשו.</span>

- <span dir="rtl">Plugin framework כללי לכל מקור חיפוש — אין לבנות framework תיאורטי. מפצלים adapter רק כאשר קיים הבדל טכני אמיתי.</span>

- <span dir="rtl">אפשרות להחליף את React ב-UI אחר — ה-API הנקי כבר משאיר אפשרות כזו; אין צורך לפתח abstraction נוסף.</span>

- <span dir="rtl">Fit thresholds לצבעים — לא קיימים. Fit % ו-Status/Color נשארים שדות נפרדים.</span>

<span dir="rtl">א.12 מבנה V1 מומלץ</span>

<span dir="rtl">החלוקה המומלצת בקוד שומרת על גבולות ברורים בלי להעמיס abstractions שאין בהם צורך כעת:</span>

- <span dir="rtl">frontend/ — React + TypeScript; pages, components, api client, hooks, types.</span>

- <span dir="rtl">backend/api/ — FastAPI endpoints ו-DTOs.</span>

- <span dir="rtl">backend/tasks/ — Task 1 ו-Task 2 כ-orchestrators בלבד; הם משתמשים בשירותים משותפים ולא משכפלים לוגיקה.</span>

- <span dir="rtl">backend/search/ ו-backend/ats/ — fetch/search + adapters לפי צורך.</span>

- <span dir="rtl">backend/dedup/ — normalization, role_key ואיחוד mirrors.</span>

- <span dir="rtl">backend/applications/ — Application Gate.</span>

- <span dir="rtl">backend/ai/ — AIProvider, OllamaProvider, schemas ו-prompts; OpenAIProvider עתידי.</span>

- <span dir="rtl">backend/coverage/ — coverage, checkpoints, continuation ו-retry state.</span>

- <span dir="rtl">backend/storage/ — SQLite וגישה מרוכזת לנתונים.</span>

- <span dir="rtl">config/ — roles, keywords, sources, batch/retry settings ו-AI provider/model.</span>

<span dir="rtl">א.13 החלטת V1 סופית</span>

<span dir="rtl">V1 תהיה מערכת Client–Server ב-React/TypeScript + FastAPI/Python. נשקיע כעת בהפרדת שכבות, מודל נתונים אחיד, API contracts, AIProvider מתחלף, schema אחיד לתשובות AI, Dedup ו-Application Gate משותפים, adapters נקודתיים ל-ATS ו-config חיצוני. לא נבנה בשלב זה authentication, PostgreSQL abstraction מלאה, Settings UI רחב, framework גנרי לכל מקור או מערכת export מורכבת. כך נשמרת גמישות עתידית בלי over-engineering. בנוסף, V1 תכלול Configuration מצומצם לעריכת רשימות עסקיות משתנות ללא שינוי קוד.</span>

<span dir="rtl">א.14 Configuration שניתן לשינוי ב-V1</span>

<span dir="rtl">עיקרון: מידע עסקי שהמשתמשת צפויה לשנות לאורך זמן יישמר כנתונים ב-DB/config ולא יהיה hard-coded בקוד. ה-UI מאפשר לערוך רק את הרשימות שהוגדרו ל-V1; ה-Backend מאמת, שומר ומספק אותן ל-Task 1/2.</span>

| <span dir="rtl">ישות</span>            | <span dir="rtl">מה היא מגדירה</span>                                | <span dir="rtl">איך משנים בעתיד</span>                                                  | <span dir="rtl">השפעה על הקוד</span>                               |
|----------------------------------------|---------------------------------------------------------------------|-----------------------------------------------------------------------------------------|--------------------------------------------------------------------|
| <span dir="rtl">Companies</span>       | <span dir="rtl">רשימת החברות ש-Task 1 סורק</span>                   | <span dir="rtl">הוספה/השבתה דרך UI; שם חברה, Careers URL, enabled ופרטים בסיסיים</span> | <span dir="rtl">ללא שינוי קוד</span>                               |
| <span dir="rtl">Search Keywords</span> | <span dir="rtl">מילות חיפוש ווריאציות שמשמשות לבניית queries</span> | <span dir="rtl">הוספה/מחיקה/השבתה של מילות חיפוש</span>                                 | <span dir="rtl">ללא שינוי קוד</span>                               |
| <span dir="rtl">Role Families</span>   | <span dir="rtl">משפחות התפקידים שנחשבות בתחום החיפוש</span>         | <span dir="rtl">הוספה/השבתה של משפחת תפקידים ושיוך מילות חיפוש</span>                   | <span dir="rtl">לרוב ללא שינוי קוד</span>                          |
| <span dir="rtl">Search Sources</span>  | <span dir="rtl">רשימת מקורות/אתרים שבהם Task 2 מחפש</span>          | <span dir="rtl">הוספת מקור Generic או השבתת מקור קיים</span>                            | <span dir="rtl">Generic: ללא קוד; אתר ייחודי: ייתכן Adapter</span> |

<span dir="rtl">א.14.1 Companies</span>

<span dir="rtl">• Task 1 לא יכיל רשימת חברות בקוד. הוא יקבל את רשימת החברות הפעילות מה-Backend.</span>

<span dir="rtl">• הוספת חברה דרך ה-UI תכניס אותה לרוטציה העתידית בלי לשנות את הקוד ובלי לשבור batch שכבר התחיל.</span>

<span dir="rtl">• לכל חברה נשמור לפחות: company_id, name, careers_url, enabled, last_scanned_at ונתוני rotation/coverage רלוונטיים.</span>

<span dir="rtl">א.14.2 Search Keywords ו-Role Families</span>

<span dir="rtl">• מילות החיפוש נשמרות כנתונים, לא בתוך פונקציות Python. Query Builder קורא אותן בכל ריצה.</span>

<span dir="rtl">• Role Family מייצגת כוונת חיפוש עסקית; לכל משפחה ניתן לשייך כמה מילות חיפוש בעברית/אנגלית.</span>

<span dir="rtl">• שינוי מילות חיפוש לא דורש deploy. אם בעתיד תשתנה המשמעות העסקית של Role Family באופן מהותי, ייתכן שנעדכן גם prompt/policy — אך לא את מנוע החיפוש עצמו.</span>

<span dir="rtl">א.14.3 Search Sources</span>

<span dir="rtl">• Search Source נשמר עם name, base_url, enabled, source_type ו-priority/metadata לפי צורך.</span>

<span dir="rtl">• מקור Generic שניתן לסרוק במנגנון הקיים ניתן להוסיף דרך UI ללא שינוי קוד.</span>

<span dir="rtl">• אתר שדורש לוגיקה מיוחדת — למשל pagination ייחודי, JavaScript חריג, login או API פרטי — מחייב Adapter חדש. הוספת הרשומה לבדה אינה מבטיחה תמיכה טכנית.</span>

<span dir="rtl">• ה-UI יציג אם מקור הוא Generic או Adapter-backed, כדי שההתנהגות תהיה ברורה.</span>

<span dir="rtl">א.14.4 גבולות ה-Configuration ב-V1</span>

<span dir="rtl">• כן לעריכה ב-UI: Companies, Search Keywords, Role Families, Search Sources.</span>

<span dir="rtl">• נשמרים ב-config/DB אך לא חייבים UI ב-V1: batch_size, retry settings, AI provider/model, scheduler.</span>

<span dir="rtl">• לא לחשוף ב-V1: SQL/DB internals, API contracts, dedup rules, Application Gate internals, schema של AI או security settings.</span>

# <span dir="rtl">נספח ב׳ — תכולת MVP</span>

## <span dir="rtl">מטרת ה-MVP</span>

<span dir="rtl">להוכיח תהליך עובד מקצה לקצה לפני השלמת כל יכולות V1: הפעלת Task 1 או Task 2 → חיפוש וגילוי → נרמול ו-Dedup → בדיקת Application Gate → ניתוח רלוונטיות והתאמה באמצעות AI → שמירת התוצאה → הצגה מסודרת ב-UI. ה-MVP שומר כבר עכשיו על הגבולות הארכיטקטוניים שקשה לשנות בדיעבד, אך מצמצם כיסוי, אוטומציה ו-UI שאפשר להוסיף אחר כך.</span>

## <span dir="rtl">ב.1 מה נכנס ל-MVP</span>

<span dir="rtl">• Client–Server מלא: React + TypeScript + Vite בצד הלקוח; FastAPI + Python בצד השרת.</span>

<span dir="rtl">• SQLite לאחסון state, runs, jobs ונתוני מערכת בסיסיים.</span>

<span dir="rtl">• מודל נתונים מרכזי ו-API contracts עבור Job, Run, Application Status ו-Job Analysis.</span>

<span dir="rtl">• Task 1 עובד על רשימת חברות חיצונית ומבצע batch/rotation בסיסי.</span>

<span dir="rtl">• Task 2 עובד בגרסה מצומצמת: Web Search/מקורות ציבוריים זמינים + ATS הנתמכים ב-MVP.</span>

<span dir="rtl">• Adapters ראשונים: Greenhouse, Lever, Comeet ו-Generic Careers Page, בכפוף לנגישות בפועל.</span>

<span dir="rtl">• Normalization + Dedup משותפים לשתי המשימות.</span>

<span dir="rtl">• Application Gate משותף לשתי המשימות מול היסטוריית ההגשות; משרה שכבר הוגשה נשארת 🔵.</span>

<span dir="rtl">• AIProvider abstraction + OllamaProvider מקומי. OpenAIProvider לא חייב להיות ממומש ב-MVP, אך הגבול המאפשר להוסיף אותו קיים.</span>

<span dir="rtl">• פלט AI לפי schema אחיד עבור relevance, fit, reasons, gaps, evidence/confidence לפי הצורך.</span>

<span dir="rtl">• Coverage בסיסי ולוג ריצות: כמה יחידות תוכננו/עובדו, משרות נמצאו, כפילויות, already-applied ושגיאות.</span>

<span dir="rtl">• UI בסיסי שמאפשר להריץ Task 1/2, לראות התקדמות/תוצאת ריצה, לצפות ברשימת משרות ולפתוח קישור למקור.</span>

<span dir="rtl">• Companies, Search Keywords, Role Families ו-Search Sources אינם hard-coded. ב-MVP ניתן לשמור אותם ב-config/DB; UI מלא לעריכתם אינו תנאי להשלמת ה-MVP.</span>

## <span dir="rtl">ב.2 מסכי MVP</span>

<span dir="rtl">• Dashboard — כפתורי Run Task 1 / Run Task 2, סטטוס הריצה האחרונה ומדדי סיכום.</span>

<span dir="rtl">• Jobs — רשימת תוצאות עם status, company, title, fit, location אם ידוע, applied status וקישור מקור.</span>

<span dir="rtl">• Run Details — progress/coverage בסיסי, מספר משרות, duplicates, already applied ושגיאות.</span>

## <span dir="rtl">ב.3 מה לא נכנס ל-MVP</span>

<span dir="rtl">• Configuration UI מלא. הרשימות ניתנות לשינוי דרך config/DB; מסכי Add/Edit ידידותיים נשארים ל-V1.</span>

<span dir="rtl">• Scheduler יומי מלא והרצות רקע אוטומטיות — ניתן להריץ ידנית ב-MVP.</span>

<span dir="rtl">• Retry/Continuation מתקדם עד מיצוי מלא של כל פער כיסוי.</span>

<span dir="rtl">• Deep Verification אוטומטי מלא: Apply path, בדיקת טופס חי, קשרי LinkedIn ואימות עמוק לכל משרה.</span>

<span dir="rtl">• כיסוי מקסימלי של כל ATS/לוח דרושים. MVP תומך במספר מקורות מייצגים כדי להוכיח את המנוע.</span>

<span dir="rtl">• OpenAI API בפועל, authentication/users, PostgreSQL, export framework ודשבורדים מתקדמים.</span>

## <span dir="rtl">ב.4 קריטריוני הצלחה ל-MVP</span>

<span dir="rtl">• אפשר להריץ Task 1 ו-Task 2 מה-UI ולקבל Run ID/סטטוס עד לסיום.</span>

<span dir="rtl">• משרות ממקורות נתמכים נכנסות למודל Job אחיד ונשמרות.</span>

<span dir="rtl">• אותה משרה שמופיעה ביותר ממקור אחד אינה מוצגת כמשרה חדשה כפולה.</span>

<span dir="rtl">• משרה שכבר הוגשה מזוהה ומסומנת 🔵 בהתאם ל-Application Gate.</span>

<span dir="rtl">• AI מסווג רלוונטיות ומחזיר Fit/Reasons/Gaps במבנה תקין שניתן לאימות בקוד.</span>

<span dir="rtl">• כשל במקור אחד אינו מוחק את תוצאות המקורות שכבר עובדו, והשגיאה מוצגת ב-Run Details.</span>

<span dir="rtl">• שינוי רשימת חברות או מילות חיפוש אינו דורש שינוי במנוע Task 1/2.</span>

## <span dir="rtl">ב.5 הערכת זמן</span>

<span dir="rtl">למפתח מנוסה שעובד באופן אינטנסיבי עם כלי AI לפיתוח: כ-8–12 ימי פיתוח נטו ל-MVP שניתן להתחיל להשתמש בו. גרסת הדגמה ראשונה עשויה להיות זמינה לאחר כשבוע עבודה; ה-buffer העיקרי נדרש לאינטגרציה ובדיקות מול אתרי Careers/ATS בפועל. ההערכה אינה כוללת פתרון ייעודי לאתרים שחוסמים אוטומציה או דורשים מנגנון התחברות מיוחד.</span>

## <span dir="rtl">ב.6 מעבר מ-MVP ל-V1</span>

<span dir="rtl">המעבר ל-V1 אמור להיות הרחבה ולא כתיבה מחדש: מוסיפים Configuration UI, scheduler, כיסוי מקורות רחב יותר, retries/continuation עמוקים, Deep Verification ויכולות נוספות. ההפרדה Client–Server, מודל הנתונים, Dedup, Application Gate ו-AIProvider נשארים ללא שינוי ארכיטקטוני מהותי.</span>
