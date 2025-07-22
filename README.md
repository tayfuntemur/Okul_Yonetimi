1. Sanal ortam oluştur:
   python -m venv venv

2. Sanal ortamı etkinleştir:
   Windows:
   venv\Scripts\activate

   Mac/Linux:
   source venv/bin/activate

3. Gereklilikleri yükle:
   pip install -r requirements.txt

4. Veritabanı oluştur:
   python manage.py migrate

5. Süper kullanıcı oluştur:

  python manage.py createsuperuser

6. Sunucuyu başlat:
   python manage.py runserver

7. Api Sunucusu Baslat:
    uvicorn main:app --reload --port 8001
