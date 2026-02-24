import pandas as pd
import numpy as np
import re
import warnings
warnings.filterwarnings("ignore")

def load_data(file_path):
    """Загрузка из Excel (слитая колонка)"""
    df = pd.read_excel(file_path, header=None)
    df.columns = ["raw"]
    expanded = df["raw"].str.split(",", expand=True)
    cols = ["FIO_owner","Company_name","INN_company","Ownership","Region","Source","Ownership_date"]
    expanded.columns = cols
    return expanded

def normalize_fio(fio):
    if pd.isna(fio) or str(fio).strip()=="": return np.nan
    parts = re.split(r"\s+", str(fio).strip())
    if len(parts)<2: return fio
    surname, *rest = parts
    initials = "".join([p[0]+"." for p in rest if p])
    return f"{surname} {initials}"

def normalize_company(name):
    if pd.isna(name): return np.nan
    cleaned = re.sub(r'["«»"]', "", str(name)).strip()
    return " ".join(cleaned.split())

def normalize_inn(inn):
    if pd.isna(inn): return np.nan
    try: return str(int(float(inn)))
    except: return np.nan

def normalize_ownership(own):
    if pd.isna(own) or str(own).strip()=="": return np.nan
    val = str(own).strip().replace("%","").replace(" ","").replace(",",".")
    try:
        num = float(val)
        return num if num<=1 else num/100
    except: return np.nan

def normalize_date(date_str):
    if pd.isna(date_str) or str(date_str).strip()=="": return pd.NaT
    s = str(date_str).strip()
    fmts = ["%d.%m.%Y","%Y-%m-%d","%d/%m/%Y","%Y%m%d","%d.%m.%y"]
    for fmt in fmts:
        try: return pd.to_datetime(s, format=fmt)
        except: continue
    return pd.to_datetime(s, errors="coerce")

def clean_data(df):
    df_clean = df.copy()
    df_clean["FIO_owner"] = df_clean["FIO_owner"].apply(normalize_fio)
    df_clean["Company_name"] = df_clean["Company_name"].apply(normalize_company)
    df_clean["INN_company"] = df_clean["INN_company"].apply(normalize_inn)
    df_clean["Ownership"] = df_clean["Ownership"].apply(normalize_ownership)
    df_clean["Ownership_date"] = df_clean["Ownership_date"].apply(normalize_date)
    df_clean["Ownership_pct"] = (df_clean["Ownership"]*100).round(1).astype(str) + "%"
    return df_clean

def analyze_data(df):
    res = {}
    # >100%
    sums = df.groupby(["Company_name","INN_company"])["Ownership"].sum()
    res["over100"] = sums[sums>1]
    # Изменения долей
    changes = df.groupby(["FIO_owner","Company_name"])["Ownership"].nunique()
    res["changing"] = changes[changes>1]
    # Мульти-владельцы
    multi = df.groupby("FIO_owner")["Company_name"].nunique()
    res["multi_owners"] = multi[multi>1]
    res["no_inn_count"] = df["INN_company"].isna().sum()
    return res, df

if __name__ == "__main__":
    df_raw = load_data("data/raw/corporate_links_raw.xlsx")
    df_clean = clean_data(df_raw)
    results, df_final = analyze_data(df_clean)
    os.makedirs("data/processed", exist_ok=True)
    df_clean.to_csv("data/processed/cleaned_data.csv", index=False)
    print("✅ Очистка завершена")
    print(f"📊 Без ИНН: {results['no_inn_count']}")
    print("🚨 >100%:", results["over100"].to_dict())
    print("🔄 Изменения:", results["changing"].to_dict())
    print("👥 Мульти-владельцы:", results["multi_owners"].to_dict())
