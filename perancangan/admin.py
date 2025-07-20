from django.contrib import admin
from .models import Profil, Proyek, Dokumen, Tugas, LaporanKemajuan

# Mendaftarkan setiap model agar muncul di halaman admin
admin.site.register(Profil)
admin.site.register(Proyek)
admin.site.register(Dokumen)
admin.site.register(Tugas)
admin.site.register(LaporanKemajuan)