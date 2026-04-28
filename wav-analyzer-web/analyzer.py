import xml.etree.ElementTree as ET
from collections import defaultdict

def analyze_xml(content):
    root = ET.fromstring(content)

    timebase = 25
    tb = root.find('.//rate/timebase')
    if tb is not None:
        try:
            timebase = float(tb.text)
        except:
            pass

    usage = defaultdict(float)
    timeline = []
    overlaps = []
    intervals = defaultdict(list)

    all_files = set()

    for f in root.findall('.//file'):
        name = f.findtext('name', '') or ''
        if any(ext in name.lower() for ext in ['.wav', '.mp3']):
            all_files.add(name)

    for clip in root.findall('.//clipitem'):
        file_el = clip.find('file')
        if file_el is None:
            continue

        name = file_el.findtext('name', '') or ''
        if not any(ext in name.lower() for ext in ['.wav', '.mp3']):
            continue

        start = float(clip.findtext('in', 0))
        end = float(clip.findtext('out', 0))
        tl_start = float(clip.findtext('start', 0))
        tl_end = float(clip.findtext('end', 0))

        dur = (end - start) / timebase

        usage[name] += dur

        timeline.append({
            "file": name,
            "start": tl_start / timebase,
            "end": tl_end / timebase,
            "duration": dur
        })

        intervals[name].append((tl_start, tl_end))

    for file, ints in intervals.items():
        ints.sort()
        for i in range(len(ints)-1):
            a = ints[i]
            b = ints[i+1]
            if b[0] < a[1]:
                overlaps.append({
                    "file": file,
                    "start": b[0]/timebase,
                    "end": min(a[1], b[1])/timebase
                })

    unused = list(all_files - set(usage.keys()))

    return usage, timeline, overlaps, unused
