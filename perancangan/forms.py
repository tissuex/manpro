from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Proyek, Tugas, Dokumen, LaporanKemajuan

class ProyekForm(forms.ModelForm):
    class Meta:
        model = Proyek
        fields = ['nama_proyek', 'lokasi', 'tanggal_mulai', 'tanggal_selesai']
        widgets = {
            'nama_proyek': forms.TextInput(attrs={'class': 'form-control'}),
            'lokasi': forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal_mulai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

class TugasForm(forms.ModelForm):
    class Meta:
        model = Tugas
        fields = ['nama_tugas', 'deskripsi', 'mandor_penanggung_jawab']
        widgets = {
            'nama_tugas': forms.TextInput(attrs={'class': 'form-control'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'mandor_penanggung_jawab': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mandor_penanggung_jawab'].queryset = User.objects.filter(profil__peran='mandor')

class DokumenForm(forms.ModelForm):
    class Meta:
        model = Dokumen
        fields = ['nama_dokumen', 'file']
        widgets = {
            'nama_dokumen': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class UpdateStatusTugasForm(forms.ModelForm):
    class Meta:
        model = Tugas
        fields = ['status']
        labels = { 'status': 'Ubah Status Pengerjaan' }
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class LaporanKemajuanForm(forms.ModelForm):
    class Meta:
        model = LaporanKemajuan
        fields = ['catatan', 'foto_kemajuan']
        labels = {
            'catatan': 'Catatan Laporan',
            'foto_kemajuan': 'Unggah Foto (Opsional)'
        }
        widgets = {
            'catatan': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'foto_kemajuan': forms.FileInput(attrs={'class': 'form-control'}),
        }

# FORM KUSTOM UNTUK REGISTRASI PENGGUNA
class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Menghilangkan teks bantuan default dari field username
        self.fields['username'].help_text = ''

        # Menambahkan styling Bootstrap ke semua field form registrasi
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs.update({
                'class': 'form-control'
            })