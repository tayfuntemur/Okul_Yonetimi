// static/admin/js/ogretmen_atama.js

document.addEventListener('DOMContentLoaded', function() {
    const sinifSelect = document.querySelector('#id_sinif_seviye');
    const derslerSelect = document.querySelector('#id_dersler_to, #id_dersler_from');
    const derslerWidget = document.querySelector('.selector');
    
    if (sinifSelect && derslerWidget) {
        console.log('Sınıf seçimi bulundu, event listener ekleniyor...');
        
        sinifSelect.addEventListener('change', function() {
            const selectedSinif = this.value;
            console.log('Seçilen sınıf:', selectedSinif);
            
            if (!selectedSinif) {
                resetDerslerWidget();
                return;
            }
            
            // Loading göstergesi ekle
            showLoading();
            
            // AJAX ile sınıfın derslerini getir
            fetch(`/ogrenciler/ajax/sinif-dersleri/?sinif_seviye=${selectedSinif}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Gelen data:', data);
                    updateDerslerWidget(data.dersler);
                    hideLoading();
                    
                    if (data.error) {
                        showMessage(data.error, 'warning');
                    } else {
                        showMessage(`${data.sinif_adi} dersler yüklendi`, 'success');
                    }
                })
                .catch(error => {
                    console.error('AJAX hatası:', error);
                    hideLoading();
                    showMessage('Dersler yüklenirken hata oluştu', 'error');
                    resetDerslerWidget();
                });
        });
    }
    
    function updateDerslerWidget(dersler) {
        // Sol taraftaki available dersler listesini güncelle
        const availableSelect = document.querySelector('#id_dersler_from');
        if (availableSelect) {
            // Mevcut seçenekleri temizle
            availableSelect.innerHTML = '';
            
            // Yeni dersleri ekle
            dersler.forEach(ders => {
                const option = document.createElement('option');
                option.value = ders.id;
                option.textContent = ders.ad;
                availableSelect.appendChild(option);
            });
            
            console.log(`${dersler.length} ders yüklendi`);
        }
    }
    
    function resetDerslerWidget() {
        // Tüm dersleri geri yükle (original state)
        const availableSelect = document.querySelector('#id_dersler_from');
        if (availableSelect) {
            // Bu kısım için server'dan tüm dersleri tekrar çekmek gerekebilir
            // Şimdilik boş bırakıyoruz
            availableSelect.innerHTML = '<option>Önce sınıf seviyesi seçin</option>';
        }
    }
    
    function showLoading() {
        const widget = document.querySelector('.selector');
        if (widget) {
            widget.style.opacity = '0.5';
            widget.style.pointerEvents = 'none';
        }
        
        // Loading spinner ekle
        if (!document.querySelector('.loading-spinner')) {
            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner';
            spinner.innerHTML = '⏳ Dersler yükleniyor...';
            spinner.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                z-index: 1000;
            `;
            widget.style.position = 'relative';
            widget.appendChild(spinner);
        }
    }
    
    function hideLoading() {
        const widget = document.querySelector('.selector');
        if (widget) {
            widget.style.opacity = '1';
            widget.style.pointerEvents = 'auto';
        }
        
        const spinner = document.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
    
    function showMessage(message, type) {
        // Mevcut mesajları kaldır
        const existingMsg = document.querySelector('.custom-message');
        if (existingMsg) {
            existingMsg.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'custom-message';
        
        let bgColor, textColor;
        switch(type) {
            case 'success':
                bgColor = '#d4edda';
                textColor = '#155724';
                break;
            case 'warning':
                bgColor = '#fff3cd';
                textColor = '#856404';
                break;
            case 'error':
                bgColor = '#f8d7da';
                textColor = '#721c24';
                break;
            default:
                bgColor = '#d1ecf1';
                textColor = '#0c5460';
        }
        
        messageDiv.style.cssText = `
            background-color: ${bgColor};
            color: ${textColor};
            padding: 8px 12px;
            border: 1px solid;
            border-radius: 4px;
            margin: 10px 0;
            font-size: 13px;
        `;
        messageDiv.textContent = message;
        
        // Sınıf seçimi alanının altına ekle
        const sinifField = document.querySelector('#id_sinif_seviye').closest('.form-row');
        if (sinifField) {
            sinifField.parentNode.insertBefore(messageDiv, sinifField.nextSibling);
        }
        
        // 3 saniye sonra mesajı kaldır
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 3000);
    }
});