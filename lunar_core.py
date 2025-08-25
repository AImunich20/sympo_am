# python code 
import math

TH_WEEK = ["อาทิตย์","จันทร์","อังคาร","พุธ","พฤหัสบดี","ศุกร์","เสาร์"]
ZODIAC = ["ชวด","ฉลู","ขาล","เถาะ","มะโรง","มะเส็ง","มะเมีย","มะแม","วอก","ระกา","จอ","กุน"]

TZ = 7.0                
CUT_HOUR = 6.0           
SYN = 29.530588853       

CAL_OFFSETS = [
    { "start": (1959, 8, 1), "end": (1960, 9, 30), "wax": 0, "wane": +1 },
    { "start": (2034, 11, 1), "end": (2035, 11, 30), "wax": 0, "wane": -1 },
    { "start": (2004, 7, 1), "end": (2011, 7, 31), "wax": +1, "wane": 0 },
]

def be(y): return y + 543

def zeller(y, m, d):
    if m <= 2:
        m += 12
        y -= 1
    K = y % 100
    J = y // 100
    h = (d + (13*(m+1))//5 + K + K//4 + J//4 + 5*J) % 7   # h: 0=Sat..6=Fri
    return (h + 6) % 7

def jd(y,m,d):
    a = (14 - m)//12
    y2 = y + 4800 - a
    m2 = m + 12*a - 3
    return float(d + ((153*m2 + 2)//5) + 365*y2 + y2//4 - y2//100 + y2//400 - 32045)

def delta_t_sec(year_decimal: float) -> float:
    if 1900 <= year_decimal <= 2100:
        return 64.7 + 64.0*((year_decimal - 2000.0)/100.0)
    return 69.0

def mean_nm(k: float) -> float:
    T = k/1236.85
    T2, T3, T4 = T*T, T*T*T, T*T*T*T
    return 2451550.09765 + SYN*k + 0.0001337*T2 - 0.000000150*T3 + 0.00000000073*T4

def true_nm_tt(k: float) -> float:
    T = k/1236.85
    E = 1 - 0.002516*T - 0.0000074*T*T
    M  = math.radians((2.5534 + 29.10535670*k - 0.0000014*T*T - 0.00000011*T*T*T) % 360)
    Mp = math.radians((201.5643 + 385.81693528*k + 0.0107582*T*T + 0.00001238*T*T*T - 0.000000058*T**4) % 360)
    F  = math.radians((160.7108 + 390.67050284*k - 0.0016118*T*T - 0.00000227*T*T*T + 0.000000011*T**4) % 360)
    Om = math.radians((124.7746 - 1.56375580*k + 0.0020691*T*T + 0.00000215*T*T*T) % 360)
    corr = (-0.40720*math.sin(Mp) + 0.17241*E*math.sin(M) + 0.01608*math.sin(2*Mp)
            + 0.01039*math.sin(2*F) + 0.00739*E*math.sin(Mp - M) - 0.00514*E*math.sin(Mp + M)
            + 0.00208*E*E*math.sin(2*M) - 0.00111*math.sin(Mp - 2*F) - 0.00057*math.sin(Mp + 2*F)
            + 0.00056*E*math.sin(2*Mp + M) - 0.00042*math.sin(3*Mp)
            + 0.00042*E*math.sin(M + 2*F) + 0.00038*E*math.sin(M - 2*F)
            - 0.00024*E*math.sin(2*Mp - M) - 0.00017*math.sin(Om))
    return mean_nm(k) + corr

def k_from_jd_tt(jd_tt: float) -> float:
    return (jd_tt - 2451550.09765) / SYN

def _in_range(y, m, d, a, b):
    return (y, m, d) >= a and (y, m, d) <= b

def lunar_day(y, m, d):
    jd0_utc = jd(y, m, d)
    sunrise_utc = jd0_utc + (CUT_HOUR - TZ) / 24.0
    sunrise_tt  = sunrise_utc + delta_t_sec(y + (m - 0.5)/12.0) / 86400.0  # TT

    k = math.floor(k_from_jd_tt(sunrise_tt))
    nm_prev = true_nm_tt(k)
    while nm_prev > sunrise_tt:
        k -= 1
        nm_prev = true_nm_tt(k)
    nm_next = true_nm_tt(k + 1)
    while nm_next <= sunrise_tt:
        k += 1
        nm_prev = true_nm_tt(k)
        nm_next = true_nm_tt(k + 1)

    syn = nm_next - nm_prev
    age = sunrise_tt - nm_prev
    month_len = 29 if round(syn) <= 29 else 30

    idx_base = int(math.floor(age))  # 0..~29

    wax_adj = 0
    wane_adj = 0
    for r in CAL_OFFSETS:
        if _in_range(y, m, d, r["start"], r["end"]):
            wax_adj  += r.get("wax", 0)
            wane_adj += r.get("wane", 0)

    if idx_base < 15:
        idx = idx_base + wax_adj
        if idx < 0: idx = 0
        phase = "ขึ้น"
        day = idx + 1
        if day > 15: day = 15
    else:
        idx = idx_base + wane_adj
        if idx < 15: idx = 15
        phase = "แรม"
        day = idx - 14
        if month_len == 29 and day > 14: day = 14
        if month_len == 30 and day > 15: day = 15
        if day < 1: day = 1

    return phase, day, k

def full_moon_k_in_may(y):
    jd_start = jd(y, 5, 1)  + (CUT_HOUR - TZ) / 24.0
    jd_end   = jd(y, 5, 31) + (CUT_HOUR - TZ) / 24.0
    tt_mid   = (jd(y, 5, 15) + (CUT_HOUR - TZ)/24.0) + delta_t_sec(y + 5.5/12.0) / 86400.0
    k0 = int(round(k_from_jd_tt(tt_mid)))

    best = None
    for dk in range(-4, 5):
        k = k0 + dk
        fm = true_nm_tt(k) + SYN/2.0
        if jd_start + delta_t_sec(y + 5/12.0)/86400.0 <= fm <= jd_end + delta_t_sec(y + 5/12.0)/86400.0:
            best = k
            break
    if best is None:
        best_k, best_diff = k0, 1e9
        for dk in range(-6, 7):
            k = k0 + dk
            fm = true_nm_tt(k) + SYN/2.0
            diff = abs(fm - tt_mid)
            if diff < best_diff:
                best_diff, best_k = diff, k
        best = best_k
    return best

def thai_month_num(y, m, d):
    phase, day, k_cur = lunar_day(y, m, d)

    k6 = full_moon_k_in_may(y)
    k6_next = full_moon_k_in_may(y + 1)
    tt_target = (jd(y, m, d) + (CUT_HOUR - TZ)/24.0) + delta_t_sec(y + (m - 0.5)/12.0) / 86400.0
    fm_y = true_nm_tt(k6) + SYN/2.0
    if tt_target < fm_y:
        k6 = full_moon_k_in_may(y - 1)
        k6_next = full_moon_k_in_may(y)

    total = k6_next - k6
    seq = [6, 7, 8] + ([8] if total == 13 else []) + [9, 10, 11, 12, 1, 2, 3, 4, 5]

    pos = k_cur - k6
    if pos < 0: pos = 0
    if pos >= total: pos = total - 1

    return seq[pos], phase, day

def zodiac(y, m, d):
    mn, _, _ = thai_month_num(y, m, d)
    base = y - 1 if mn < 5 else y
    return ZODIAC[(base - 1984) % 12]

def thai_date(y, m, d):
    wd_name = TH_WEEK[zeller(y, m, d)]
    month_num, phase, k = thai_month_num(y, m, d)
    be_year = y + 543
    return f"{wd_name} {d:02d}/{m:02d}/{y} (พ.ศ.{be_year}) → {phase} {k} ค่ำ เดือน {month_num} {zodiac(y,m,d)}"

def function_thai(lsdate):
    for y, m, d in lsdate:
        print(thai_date(y, m, d))
# if __name__ == "__main__":
#     samples = [
#         (1959, 8, 25),
#         (1984, 1, 7),
#         (2004, 7, 20),
#         (2007, 7, 20),
#         (2010, 7, 20),
#         (2025, 8, 25),
#     ]
#     # for y, m, d in samples:
#     #     print(thai_date(y, m, d))
#     function_thai(samples)