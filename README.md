# Анализ корпоративных связей

## Задача
Очистка и анализ данных владельцев компаний из corporate_links_raw.xlsx [file:1]

**Выполнено:**
-  ФИО: Фамилия И.О.
-  Компании: без кавычек  
-  ИНН: str тип, найдены пропуски (2)
-  Ownership: % → float (0.5=50%)
-  Даты: YYYY-MM-DD

**Аномалии:**
- Сумма >100%: ООО "Лютик" (130%)
- Изменения долей: Орлов Д.Д.
- Мульти-владельцы: Иванов И.И. (3 компании)

## Запуск
```bash
pip install -r requirements.txt  
python src/data_cleaning.py
jupyter notebook notebooks/analysis.ipynb
```

Результат: `data/processed/cleaned_data.csv`
