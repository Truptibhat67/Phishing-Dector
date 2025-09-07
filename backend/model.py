from __future__ import annotations
import re, math, json
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import tldextract
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

BASE = Path(__file__).parent
MODEL_PATH = BASE / "model.pkl"

SUSPICIOUS_TLDS = {
    "ru","tk","cn","ga","cf","ml","gq","work","top","xyz","link","click","country"
}
KEYWORDS = [
    "login","verify","update","secure","account","bank","support","limited","confirm",
    "apple","paypal","microsoft","amazon","prize","winner","free","gift","download"
]

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    from collections import Counter
    counts = Counter(s)
    length = len(s)
    return -sum((c/length) * math.log2(c/length) for c in counts.values())

def extract_features(url: str) -> Dict[str, float]:
    url = url.strip()
    parsed = tldextract.extract(url)
    domain = f"{parsed.domain}.{parsed.suffix}" if parsed.suffix else parsed.domain
    subdomain = parsed.subdomain or ""
    host = ".".join([p for p in [subdomain, domain] if p])
    path = ""
    try:
        path = re.sub(r"^https?://", "", url, flags=re.I)
    except Exception:
        pass

    has_ip = 1.0 if re.search(r"(\d{1,3}\.){3}\d{1,3}", url) else 0.0
    has_at = 1.0 if "@" in url else 0.0
    has_dash = 1.0 if "-" in parsed.domain else 0.0
    num_sub = subdomain.count(".") + (1 if subdomain else 0)
    tld = parsed.suffix.lower()
    tld_susp = 1.0 if tld in SUSPICIOUS_TLDS else 0.0
    length = len(url)
    num_digits = sum(ch.isdigit() for ch in url)
    num_spec = sum(ch in "._-@?&=%" for ch in url)
    keyword_hits = sum(1 for kw in KEYWORDS if kw in url.lower())
    host_entropy = shannon_entropy(host)
    uses_https = 1.0 if url.lower().startswith("https://") else 0.0
    num_params = url.count("=")
    long_path = 1.0 if len(url.split("/", 3)[-1]) > 60 else 0.0

    feats = {
        "length": float(length),
        "num_digits": float(num_digits),
        "num_specials": float(num_spec),
        "num_subdomains": float(num_sub),
        "has_ip": has_ip,
        "has_at": has_at,
        "has_dash_in_domain": has_dash,
        "suspicious_tld": tld_susp,
        "keyword_hits": float(keyword_hits),
        "host_entropy": float(host_entropy),
        "uses_https": uses_https,
        "num_params": float(num_params),
        "long_path": long_path,
    }
    return feats

@dataclass
class URLModel:
    clf: Any
    feature_names: List[str]

    def predict_with_explain(self, url: str) -> Dict[str, Any]:
        feats = extract_features(url)
        X = np.array([[feats[f] for f in self.feature_names]], dtype=float)
        proba = float(self.clf.predict_proba(X)[0,1])
        label = "phishing" if proba >= 0.5 else "legit"

        # Explain with coefficient contributions (log-odds space)
        coef = self.clf.coef_[0]
        intercept = self.clf.intercept_[0]
        contributions = [(name, float(val*coef[i])) for i,(name,val) in enumerate(zip(self.feature_names, X[0]))]
        # Sort by absolute contribution to log-odds
        top = sorted(
            [{"feature": n, "value": float(v), "logit_contribution": float(c)} for (n,c), v in zip(zip(self.feature_names, coef), X[0])],
            key=lambda d: abs(d["logit_contribution"]),
            reverse=True
        )[:5]

        return {
            "url": url,
            "pred_label": label,
            "pred_proba": proba,
            "features": feats,
            "top_contributors": top
        }

def load_sample_dataset() -> pd.DataFrame:
    # Small curated demo dataset (URLs, labels 1=phish, 0=legit)
    rows = []
    legit = [
        "https://www.google.com/",
        "https://www.microsoft.com/en-us/",
        "https://www.apple.com/",
        "https://www.amazon.com/",
        "https://www.paypal.com/signin",
        "https://accounts.google.com/ServiceLogin",
        "https://www.wikipedia.org/",
        "https://developer.mozilla.org/en-US/",
        "https://www.npmjs.com/package/react",
        "https://github.com/",
        "https://docs.python.org/3/",
        "https://www.bankofamerica.com/",
        "https://www.hsbc.com/",
        "https://www.tesla.com/",
        "https://www.intuit.com/",
        "https://www.netflix.com/",
    ]
    phish = [
        "http://paypal.verify-login.secure-update.com/login",
        "http://update-account-amazon.com/secure/?id=12345",
        "http://apple-id.support-verify.com/login.php",
        "http://bankofamerica.com.secure-update.tk/verify",
        "http://192.168.1.10/confirm/credential.php",
        "http://secure-login-paypaI.com/",  
        "http://google.com-support-login.top/verify",
        "http://microsoft-support-security.xyz/update",
        "http://secure.account-confirm.cf/login",
        "http://winner-free-gift.ga/claim?id=999",
        "http://verify-update-login.link/?a=1&b=2&c=3&d=4&e=5",
        "http://support-amaz0n.work/login",
        "http://limited-offer-prize.gq/free",
        "http://secure-update-bank.ml/auth",
        "http://confirm-appleid.click/",
        "http://support.apple.com.example.com.verify.ru/login",
        "https://docs.google.com/presentation/d/e/2PACX-1vTVj7OXwAUKJDv57jBmVg8eWFIUvTQ3c0-F1gPD_G5CwsQzOf3aelTqo4q42FIlqbHODnIlx2-Lx3Cf/pub?start=false&loop=false&delayms=3000&slide=id.p",
        "http://electrocoolhvacr.com/control/163/163xffrxxzzz.htm",
        "http://electrocoolhvacr.com/control/163/163xffrxxzzz.htm",
        "https://ersfilter-my.sharepoint.com/personal/nradonich_ersfilter_com/_layouts/15/WopiFrame.aspx?guestaccesstoken=6yWMLBQi9%2bSJfgzhADHvte2gYoWjf83IQBjRjehiK4s%3d&docid=1_135f7008dfbfa44e6b09dab0eb165b997&wdFormId=%7BE037F2D9%2D5DAA%2D4916%2DBA03%2DEB11D0AA6DEA%7D&action=formsubmit",
        "http://electrocoolhvacr.com/control/163/163xffrxxzzz.htm",
        "https://docs.google.com/presentation/d/e/2PACX-1vTVj7OXwAUKJDv57jBmVg8eWFIUvTQ3c0-F1gPD_G5CwsQzOf3aelTqo4q42FIlqbHODnIlx2-Lx3Cf/pub?start=false&loop=false&delayms=3000&slide=id.p",
        "https://btttelecommunniccatiion.weeblysite.com/",
        "https://kq0hgp.webwave.dev/",
        "https://brittishtele1bt-69836.getresponsesite.com/",
        "https://bt-internet-105056.weeblysite.com/",
        "https://teleej.weebly.com/",
        "https://maryleyshon.wixsite.com/my-site-1",
        "https://chamakhman.wixsite.com/my-site-4",
        "https://posts-ch.buzz/ch/",
        "https://tinyurl.com/bdfpfyur",
        "https://www.msaaezusshubsnsk.top",
        "https://www.msaaezusshubsnk.top",
        "https://www.msaaezuhubsnk.top",
        "https://docs.google.com/presentation/d/e/2PACX-1vSQhRfmHabALkn-AOLiTaZqD56SkYdFCKmKaqIrGG3EFFH6gZWKhJat2O1j5aFmxrSVAbYiXsWqB1_v/pub?start=false&loop=false&delayms=3000&slide=id.p",
        "https://docs.google.com/presentation/d/e/2PACX-1vSG51ZslCaXw4PrBW46kFU0Tlq4lYzrRyN40Lh_pEQ0ASpzDWxYjihI6-rcgu9U29weJY-0s_79Bk4T/pub?start=false&loop=false&delayms=3000&slide=id.p",
        "https://docs.google.com/presentation/d/e/2PACX-1vQdsu4PGmnYNi1qRHMH7GdUapyKZdxRSBr3lYwoHRGHj2wiu1nSWS5eGxC2N6jYJyQZpTrI1palx_2O/pub?start=false&loop=false&delayms=3000&slide=id.p",
        "https://us10.list-manage.com/survey?u=f5e2489ff9b1eb9c05b8e12b3&id=8b1b0686bc&e=",
        "https://loginaccountverifice392.square.site/",
        "https://tqwip3lbk5.onrocket.site/ch/index2.php",
        "https://pub-19aa984b0fb848bea6ffcc9634982332.r2.dev/email.upgrade.html#test@example.com",
        "https://10olixo.weeblysite.com/",
        "https://d-106596.weeblysite.com/",
        "https://managing55.wixsite.com/my-site",
        "https://www.aeombamk.co.nlgvsfig.com/",
        "https://postms.top/kUquEi/",
        "https://uteta.org/wp-includes/js/",
        "https://mysunrise-app-mip-appsuite.codeanyapp.com/wp-content/sunrise/index.html",
        "https://7q-4xu.cfd/ai/?oferta/zegarek-firmy-alkor-adriatica?navCategoryId=&amp;t=1711954905542",
        "https://ormpu.cn",
        "https://docs.google.com/presentation/d/e/2PACX-1vTVj7OXwAUKJDv57jBmVg8eWFIUvTQ3c0-F1gPD_G5CwsQzOf3aelTqo4q42FIlqbHODnIlx2-Lx3Cf/pub?start=false&loop=false&delayms=3000",
        "https://tinyurl.com/y6ed8sx8",
        "https://docs.google.com/presentation/d/e/2PACX-1vS60bmjSsSkqTqreCKIVQCxFGpZiDuIKqSdIWSVWB0Mf7c0y-b_Yqyj5AMD1FxrRDOYwEpVGc3RJ8fl/pub?start=false&loop=false&delayms=3000",
        "https://www.zrkhopdi.com",
        "https://docs.google.com/presentation/d/e/2PACX-1vRq9XcQhWixRbox-KPUbFd28GDEy9_VdF1xCZZIKJFoK2aRwtt9UneD690Ls0toNNYVF3YvIymt3YXW/pub?start=false&loop=false&delayms=3000",
        "https://docs.google.com/presentation/d/e/2PACX-1vR5JcFRJpccReGWw4DkwCuEhlEiPjChb3e9fp6MrccPIYNngjn1-NbPpKhrFKb6i_swBKlt3ZyF6Wt9/pub?start=false&loop=false&delayms=3000&slide=id.p",
        "https://us9.list-manage.com/survey?u=39b1647b88ecd5419f2f74923&id=3dabfe7ee8&e",
        "https://safeloggingin.com/voicemail.btlandline.com/?email=",
        "https://www.ligolesht-othole.youdontcare.com/",
        "https://www.duryorice-rime.acmetoy.com/",
        "https://www.quidjusck-just.serveuser.com/",
        "https://www.soturiund-ming.otzo.com/",
        "https://www.traompvel-book.ygto.com/",
        "https://www.haveable-busin.gettrials.com/",
        "https://www.kepolyeps-packin.ocry.com/",
        "https://www.inarcalud-dry.misecure.com/",
        "https://www.alsanshye-and.dsmtp.com/",
        "https://www.shioverp-youre.myddns.com/",
        "https://www.arerolght-wallet.ourhobby.com/",
        "https://www.mulastsic-your.americanunfinished.com/",
        "https://www.shapanye-discon.freeddns.com/",
        ]
    for u in legit:
        rows.append({"url": u, "label": 0})
    for u in phish:
        rows.append({"url": u, "label": 1})
    df = pd.DataFrame(rows)

    extras = []
    for u in phish[:10]:
        extras.append({"url": u + "&extra=param"*5, "label": 1})
    for u in legit[:10]:
        extras.append({"url": u + "docs/" + "a"*40, "label": 0})
    df = pd.concat([df, pd.DataFrame(extras)], ignore_index=True)
    return df

def train_or_load() -> URLModel:
    if MODEL_PATH.exists():
        clf = joblib.load(MODEL_PATH)
        return URLModel(clf=clf, feature_names=list(extract_features("https://example.com").keys()))
    # Training
    df = load_sample_dataset()
    feat_rows = []
    for url, label in zip(df["url"], df["label"]):
        feats = extract_features(url)
        feats["label"] = label
        feat_rows.append(feats)
    feat_df = pd.DataFrame(feat_rows)
    X = feat_df.drop(columns=["label"]).values
    y = feat_df["label"].values
    clf = LogisticRegression(max_iter=200)
    clf.fit(X, y)
    # Save
    joblib.dump(clf, MODEL_PATH)
    
    try:
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        clf2 = LogisticRegression(max_iter=200).fit(Xtr, ytr)
        ypred = clf2.predict(Xte)
        print(classification_report(yte, ypred))
    except Exception as e:
        print("Eval skipped:", e)
    return URLModel(clf=clf, feature_names=[c for c in feat_df.columns if c != "label"])

def ensure_model() -> URLModel:
    return train_or_load()
