# perancangan/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import ProyekForm, TugasForm, DokumenForm, UpdateStatusTugasForm, LaporanKemajuanForm, CustomUserCreationForm
from .models import Proyek, Tugas, Profil, Dokumen, LaporanKemajuan
from django.utils import timezone
from django.db.models import Q # <-- Pastikan Q diimpor

### HALAMAN PEMILIHAN PERAN ###
class PilihPeranView(TemplateView):
    template_name = 'perancangan/pilih_peran.html'

### HALAMAN OTENTIKASI (LOGIN, REGISTRASI) ###
class CustomLoginView(LoginView):
    template_name = 'perancangan/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['peran'] = self.request.GET.get('peran', 'arsitek')
        return context

    def get_success_url(self):
        user = self.request.user
        if hasattr(user, 'profil'):
            if user.profil.peran == 'arsitek':
                return reverse_lazy('perancangan:dashboard_arsitek')
            elif user.profil.peran == 'mandor':
                return reverse_lazy('perancangan:dashboard_mandor')
        return reverse_lazy('pilih_peran')

class RegistrasiView(View):
    def get(self, request, *args, **kwargs):
        # Gunakan form kustom untuk registrasi
        form = CustomUserCreationForm()
        peran = request.GET.get('peran')
        context = {'form': form, 'peran': peran}
        return render(request, 'perancangan/registrasi.html', context)

    def post(self, request, *args, **kwargs):
        form = CustomUserCreationForm(request.POST)
        peran = request.POST.get('peran')
        if form.is_valid():
            user = form.save()
            if peran in ['arsitek', 'mandor']:
                Profil.objects.create(user=user, peran=peran)
            return redirect(f"{reverse_lazy('perancangan:login')}?peran={peran}")
        else:
            context = {'form': form, 'peran': peran}
            return render(request, 'perancangan/registrasi.html', context)

### HALAMAN DASHBOARD SESUAI PERAN ###
@login_required
def dashboard_arsitek(request):
    if not hasattr(request.user, 'profil') or request.user.profil.peran != 'arsitek':
        return redirect('pilih_peran')
        
    semua_proyek = Proyek.objects.filter(arsitek=request.user)
    tanggal_hari_ini = timezone.now().date()

    # Logika penghitungan yang diperbaiki
    total_proyek = semua_proyek.count()
    
    # Proyek selesai: yang punya tanggal selesai DAN tanggalnya adalah hari ini atau sebelumnya.
    proyek_selesai = semua_proyek.filter(
        tanggal_selesai__isnull=False, 
        tanggal_selesai__lte=tanggal_hari_ini
    ).count()

    # Proyek aktif: adalah sisa dari total proyek dikurangi proyek yang selesai.
    proyek_aktif = total_proyek - proyek_selesai
    
    context = {
        'proyek_saya': semua_proyek,
        'total_proyek': total_proyek,
        'proyek_aktif': proyek_aktif,
        'proyek_selesai': proyek_selesai,
        'tanggal_hari_ini': tanggal_hari_ini, # Kirim tanggal agar bisa dipakai di template
    }
    return render(request, 'perancangan/dashboard_arsitek.html', context)

@login_required
def dashboard_mandor(request):
    if not hasattr(request.user, 'profil') or request.user.profil.peran != 'mandor':
        return redirect('pilih_peran')

    tugas_list = Tugas.objects.filter(mandor_penanggung_jawab=request.user)
    context = {
        'tugas_saya': tugas_list,
    }
    return render(request, 'perancangan/dashboard_mandor.html', context)

### HALAMAN KELOLA DATA ###
@login_required
def tambah_proyek(request):
    if request.method == 'POST':
        form = ProyekForm(request.POST)
        if form.is_valid():
            proyek = form.save(commit=False)
            proyek.arsitek = request.user
            proyek.save()
            return redirect('perancangan:dashboard_arsitek')
    else:
        form = ProyekForm()
    
    return render(request, 'perancangan/tambah_proyek.html', {'form': form})

@login_required
def detail_proyek(request, proyek_id):
    proyek = get_object_or_404(Proyek, id=proyek_id)
    tugas_proyek = Tugas.objects.filter(proyek=proyek)
    dokumen_proyek = Dokumen.objects.filter(proyek=proyek)
    
    context = {
        'proyek': proyek,
        'tugas_list': tugas_proyek,
        'dokumen_list': dokumen_proyek,
    }
    return render(request, 'perancangan/detail_proyek.html', context)

@login_required
def tambah_tugas(request, proyek_id):
    proyek = get_object_or_404(Proyek, id=proyek_id)
    if request.method == 'POST':
        form = TugasForm(request.POST)
        if form.is_valid():
            tugas = form.save(commit=False)
            tugas.proyek = proyek
            tugas.save()
            return redirect('perancangan:detail_proyek', proyek_id=proyek.id)
    else:
        form = TugasForm()

    return render(request, 'perancangan/tambah_tugas.html', {'form': form, 'proyek': proyek})

@login_required
def unggah_dokumen(request, proyek_id):
    proyek = get_object_or_404(Proyek, id=proyek_id)
    if request.method == 'POST':
        form = DokumenForm(request.POST, request.FILES)
        if form.is_valid():
            dokumen = form.save(commit=False)
            dokumen.proyek = proyek
            dokumen.diunggah_oleh = request.user
            dokumen.save()
            return redirect('perancangan:detail_proyek', proyek_id=proyek.id)
    else:
        form = DokumenForm()
    
    return render(request, 'perancangan/unggah_dokumen.html', {'form': form, 'proyek': proyek})

@login_required
def detail_tugas(request, tugas_id):
    tugas = get_object_or_404(Tugas, id=tugas_id)
    
    if tugas.mandor_penanggung_jawab != request.user:
        return redirect('perancangan:dashboard_mandor')

    if request.method == 'POST':
        if 'update_status' in request.POST:
            form_status = UpdateStatusTugasForm(request.POST, instance=tugas)
            if form_status.is_valid():
                form_status.save()
        
        elif 'kirim_laporan' in request.POST:
            form_laporan = LaporanKemajuanForm(request.POST, request.FILES)
            if form_laporan.is_valid():
                laporan = form_laporan.save(commit=False)
                laporan.tugas = tugas
                laporan.dibuat_oleh = request.user
                laporan.save()

        return redirect('perancangan:detail_tugas', tugas_id=tugas.id)

    form_status = UpdateStatusTugasForm(instance=tugas)
    form_laporan = LaporanKemajuanForm()
    
    laporan_list = LaporanKemajuan.objects.filter(tugas=tugas).order_by('-tanggal_laporan')
    
    context = {
        'tugas': tugas,
        'laporan_list': laporan_list,
        'form_status': form_status,
        'form_laporan': form_laporan,
    }
    return render(request, 'perancangan/detail_tugas.html', context)

@login_required
def detail_tugas_arsitek(request, tugas_id):
    tugas = get_object_or_404(Tugas, id=tugas_id)
    
    if tugas.proyek.arsitek != request.user:
        return redirect('perancangan:dashboard_arsitek')

    laporan_list = LaporanKemajuan.objects.filter(tugas=tugas).order_by('-tanggal_laporan')
    
    context = {
        'tugas': tugas,
        'laporan_list': laporan_list,
    }
    return render(request, 'perancangan/detail_tugas_arsitek.html', context)

@login_required
def konfirmasi_proyek_selesai(request, proyek_id):
    if request.method == 'POST':
        proyek = get_object_or_404(Proyek, id=proyek_id)
        
        if proyek.arsitek == request.user:
            proyek.tanggal_selesai = timezone.now().date()
            proyek.save()
            
    return redirect('perancangan:detail_proyek', proyek_id=proyek_id)

# Anda belum memiliki view ini, jadi saya tambahkan
@login_required
def verifikasi_tugas_selesai(request, tugas_id):
    if request.method == 'POST':
        tugas = get_object_or_404(Tugas, id=tugas_id)
        
        if tugas.proyek.arsitek == request.user:
            tugas.status = 'diverifikasi'
            tugas.save()
            
    return redirect('perancangan:detail_tugas_arsitek', tugas_id=tugas_id)