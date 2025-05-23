# TUGAS BIG DATA
📋 Tugas Mahasiswa
1. Buat Topik Kafka<br>
Buat dua topik di Apache Kafka:
sensor-suhu-gudang
sensor-kelembaban-gudang
<br>Topik ini akan digunakan untuk menerima data dari masing-masing sensor secara real-time.

2. Simulasikan Data Sensor (Producer Kafka)<br>
Buat dua Kafka producer terpisah:<br>
a. Producer Suhu
Kirim data setiap detik
Format:
{"gudang_id": "G1", "suhu": 82}<br>
b. Producer Kelembaban
Kirim data setiap detik
Format:
{"gudang_id": "G1", "kelembaban": 75}
Gunakan minimal 3 gudang: G1, G2, G3.

3. Konsumsi dan Olah Data dengan PySpark<br>
a. Buat PySpark Consumer
Konsumsi data dari kedua topik Kafka.<br>
b. Lakukan Filtering:
Suhu > 80°C → tampilkan sebagai peringatan suhu tinggi<br>
Kelembaban > 70% → tampilkan sebagai peringatan kelembaban tinggi<br>
Contoh Output:
```
[Peringatan Suhu Tinggi]
Gudang G2: Suhu 85°C
[Peringatan Kelembaban Tinggi]
Gudang G3: Kelembaban 74%
```

5. Gabungkan Stream dari Dua Sensor
Lakukan join antar dua stream berdasarkan gudang_id dan window waktu (misalnya 10 detik) untuk mendeteksi kondisi bahaya ganda.
c. Buat Peringatan Gabungan:
Jika ditemukan suhu > 80°C dan kelembaban > 70% pada gudang yang sama, tampilkan peringatan kritis.

✅ Contoh Output Gabungan:
[PERINGATAN KRITIS]
Gudang G1:
- Suhu: 84°C
- Kelembaban: 73%
- Status: Bahaya tinggi! Barang berisiko rusak

Gudang G2:
- Suhu: 78°C
- Kelembaban: 68%
- Status: Aman

Gudang G3:
- Suhu: 85°C
- Kelembaban: 65%
- Status: Suhu tinggi, kelembaban normal

Gudang G4:
- Suhu: 79°C
- Kelembaban: 75%
- Status: Kelembaban tinggi, suhu aman
🎓 Tujuan Pembelajaran
Mahasiswa diharapkan dapat:

Memahami cara kerja Apache Kafka dalam pengolahan data real-time.

Membuat Kafka Producer dan Consumer untuk simulasi data sensor.

Mengimplementasikan stream filtering dengan PySpark.

Melakukan join multi-stream dan analisis gabungan dari berbagai sensor.

Mencetak hasil analitik berbasis kondisi kritis gudang ke dalam output console.



![image](https://github.com/user-attachments/assets/9f99d90b-a29a-4a5e-b0bf-7af43a35b320)

![image](https://github.com/user-attachments/assets/e822173c-a902-4f7c-85e6-3f1ff4e48cf0)
![image](https://github.com/user-attachments/assets/ee504be4-42fe-4432-b703-caf69f2375d6)

![image](https://github.com/user-attachments/assets/25579f28-615d-4602-8736-a7c55b91abcf)
![image](https://github.com/user-attachments/assets/5d23ee12-31e4-49c1-8b47-7006906a20dc)

