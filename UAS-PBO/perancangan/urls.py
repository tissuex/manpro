# perancangan/urls.py

from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

# Memberi nama pada grup URL ini agar tidak bentrok dengan aplikasi lain
app_name = 'perancangan'

urlpatterns = [
    # === URL Otentikasi ===
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='pilih_peran'), name='logout'),
    path('registrasi/', views.RegistrasiView.as_view(), name='registrasi'),
    
    # === URL Dashboard (sesuai peran) ===
    path('dashboard/arsitek/', views.dashboard_arsitek, name='dashboard_arsitek'),
    path('dashboard/mandor/', views.dashboard_mandor, name='dashboard_mandor'),

    path('proyek/tambah/', views.tambah_proyek, name='tambah_proyek'),
    # === URL Detail Proyek ===
    path('proyek/<int:proyek_id>/', views.detail_proyek, name='detail_proyek'),
    # URL untuk menambah tugas baru, perlu proyek_id
    path('proyek/<int:proyek_id>/tambah-tugas/', views.tambah_tugas, name='tambah_tugas'),
    # URL untuk mengunggah dokumen
    path('proyek/<int:proyek_id>/unggah-dokumen/', views.unggah_dokumen, name='unggah_dokumen'),
    # URL melihat detail tugas
    path('tugas/<int:tugas_id>/', views.detail_tugas, name='detail_tugas'),
    # URL untuk Arsitek melihat detail tugas
    path('arsitek/tugas/<int:tugas_id>/', views.detail_tugas_arsitek, name='detail_tugas_arsitek'),
    # URL untuk konfirmasi proyek selesai
    path('proyek/<int:proyek_id>/konfirmasi-selesai/', views.konfirmasi_proyek_selesai, name='konfirmasi_proyek_selesai'),
]