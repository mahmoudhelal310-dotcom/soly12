#!/usr/bin/env python3
"""إضافة ابتهالات إلى فهرس الموقع (yaqeen-mahmoud-helal/ibtihal-data.js).
الاستعمال:
  python3 tools/add_ibtihal.py "الشيخ سيد النقشبندي" https://youtu.be/XXXXXXXXXXX
  python3 tools/add_ibtihal.py "الشيخ سيد النقشبندي" "https://www.youtube.com/playlist?list=PLxxxxxxxx"
رابط فيديو مفرد أو عدة روابط، أو رابط قائمة تشغيل كاملة (list=...) فيضيف كل فيديوهاتها دفعة واحدة.
يجلب العنوان تلقائياً من يوتيوب (بدون مفتاح API)."""
import sys, re, json, urllib.request, urllib.parse
P = "yaqeen-mahmoud-helal/ibtihal-data.js"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")

def oembed_title(vid):
    try:
        u = "https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote("https://www.youtube.com/watch?v=" + vid)
        return json.load(urllib.request.urlopen(u, timeout=15))["title"]
    except Exception:
        return None

def expand_playlist(list_id):
    """يستخرج أرقام الفيديوهات من صفحة قائمة التشغيل العامة (بأكثر من طريقة احتياطية)، ثم يجلب عنوان كل فيديو عبر oEmbed."""
    html = fetch("https://www.youtube.com/playlist?list=" + list_id)
    ids = re.findall(r'"playlistVideoRenderer":\{"videoId":"([\w-]{11})"', html)
    if not ids:
        ids = re.findall(r'"videoId":"([\w-]{11})"', html)
    seen, ordered = set(), []
    for v in ids:
        if v not in seen:
            seen.add(v); ordered.append(v)
    return ordered

def main():
    if len(sys.argv) < 3:
        print(__doc__); return
    reciter, links = sys.argv[1], sys.argv[2:]
    src = open(P, encoding="utf-8").read()
    m = re.search(r"window\.IBTIHAL_DATA=(\[.*\]);", src, re.S)
    data = json.loads(m.group(1)); have = {x["v"] for x in data}
    added = 0
    for link in links:
        lm = re.search(r"[?&]list=([\w-]+)", link)
        if lm and "watch?v=" not in link:
            print("جاري قراءة قائمة التشغيل…")
            try:
                ids = expand_playlist(lm.group(1))
            except Exception as e:
                print("تعذّر قراءة قائمة التشغيل:", e); continue
            if not ids:
                print("لم أجد فيديوهات في القائمة (قد تكون خاصة أو تغيّر شكل صفحة يوتيوب)."); continue
            print(f"وجدت {len(ids)} فيديو، جاري جلب العناوين (قد يستغرق دقيقة)…")
            for vid in ids:
                if vid in have:
                    continue
                title = oembed_title(vid)
                if not title:
                    print("تعذّر جلب عنوان", vid, "- تم تخطيه"); continue
                data.append({"t": title, "r": reciter, "v": vid}); have.add(vid); added += 1
                print("أضيف:", title)
            continue
        vm = re.search(r"(?:v=|youtu\.be/|embed/|shorts/)([\w-]{11})", link) or re.fullmatch(r"([\w-]{11})", link)
        if not vm:
            print("رابط غير مفهوم:", link); continue
        vid = vm.group(1)
        if vid in have:
            print("موجود:", vid); continue
        title = oembed_title(vid) or input(f"تعذّر جلب العنوان لـ {vid}، اكتبه: ")
        data.append({"t": title, "r": reciter, "v": vid}); have.add(vid); added += 1
        print("أضيف:", title)
    if added:
        open(P, "w", encoding="utf-8").write("window.IBTIHAL_DATA=" + json.dumps(data, ensure_ascii=False, indent=0) + ";\n")
        print(f"تم حفظ {added} ابتهالاً جديداً. ارفع yaqeen-mahmoud-helal/ibtihal-data.js على الموقع.")
    else:
        print("لم تُضَف عناصر جديدة.")

if __name__ == "__main__":
    main()
