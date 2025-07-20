from django.db import models
from django.contrib.auth.models import User

# Model untuk menyimpan informasi tambahan user, seperti perannya
class Profil(models.Model):
    ROLE_CHOICES = (
        ('arsitek', 'Arsitek'),
        ('mandor', 'Mandor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    peran = models.CharField(max_length=10, choices=ROLE_CHOICES)
    nomor_telepon = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_peran_display()}"

# Model utama untuk setiap Proyek Pembangunan
class Proyek(models.Model):
    nama_proyek = models.CharField(max_length=200)
    lokasi = models.CharField(max_length=255)
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField(null=True, blank=True)
    arsitek = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='proyek_arsitek')
    mandor_bertugas = models.ManyToManyField(User, related_name='proyek_mandor', blank=True)

    def __str__(self):
        return self.nama_proyek

# Model untuk dokumen yang terkait dengan proyek (RAB, Blueprint)
class Dokumen(models.Model):
    proyek = models.ForeignKey(Proyek, on_delete=models.CASCADE, related_name='dokumen')
    nama_dokumen = models.CharField(max_length=100)
    file = models.FileField(upload_to='dokumen/%Y/%m/%d/')
    diunggah_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tanggal_unggah = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nama_dokumen

# Model untuk setiap tugas dalam sebuah proyek
class Tugas(models.Model):
    STATUS_CHOICES = (
        ('belum', 'Belum Dikerjakan'),
        ('dikerjakan', 'Sedang Dikerjakan'),
        ('selesai', 'Selesai'),
        ('revisi', 'Butuh Revisi'),
    )
    proyek = models.ForeignKey(Proyek, on_delete=models.CASCADE, related_name='tugas')
    nama_tugas = models.CharField(max_length=200)
    deskripsi = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='belum')
    mandor_penanggung_jawab = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tugas_mandor')
    
    def __str__(self):
        return self.nama_tugas

# Model untuk laporan kemajuan dari Mandor
class LaporanKemajuan(models.Model):
    tugas = models.ForeignKey(Tugas, on_delete=models.CASCADE, related_name='laporan')
    catatan = models.TextField()
    foto_kemajuan = models.ImageField(upload_to='laporan/%Y/%m/%d/', null=True, blank=True)
    dibuat_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tanggal_laporan = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Laporan untuk {self.tugas.nama_tugas} pada {self.tanggal_laporan.strftime('%d-%m-%Y')}"