document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    
    if (!calendarEl) {
        return;
    }

    // カレンダーの初期化
    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'ja',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        events: '/api/reservations',
        eventClick: function(info) {
            alert('予約詳細: ' + info.event.title);
        },
        dateClick: function(info) {
            // 日付クリック時の処理
            if (document.getElementById('date')) {
                document.getElementById('date').value = info.dateStr;
            }
        },
        businessHours: {
            daysOfWeek: [1, 2, 3, 4, 5, 6], // 月曜日から土曜日
            startTime: '09:00',
            endTime: '18:00'
        },
        selectConstraint: 'businessHours',
        eventConstraint: 'businessHours',
        height: 'auto',
        eventDisplay: 'block',
        dayMaxEvents: 3,
        moreLinkClick: 'popover'
    });

    calendar.render();

    // 予約フォームの処理
    var reservationForm = document.getElementById('reservationForm');
    if (reservationForm) {
        reservationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            var formData = {
                date: document.getElementById('date').value,
                start_time: document.getElementById('startTime').value,
                end_time: document.getElementById('endTime').value,
                purpose: document.getElementById('purpose').value
            };
            
            // バリデーション
            if (!formData.date || !formData.start_time || !formData.end_time || !formData.purpose) {
                showAlert('すべての項目を入力してください。', 'warning');
                return;
            }
            
            if (formData.start_time >= formData.end_time) {
                showAlert('終了時間は開始時間より後にしてください。', 'warning');
                return;
            }
            
            // 選択日が今日以前かチェック
            var selectedDate = new Date(formData.date);
            var today = new Date();
            today.setHours(0, 0, 0, 0);
            
            if (selectedDate < today) {
                showAlert('過去の日付は選択できません。', 'warning');
                return;
            }
            
            // 予約処理
            fetch('/api/reserve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert(data.message, 'success');
                    reservationForm.reset();
                    calendar.refetchEvents(); // カレンダー更新
                } else {
                    showAlert(data.message, 'danger');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('予約処理中にエラーが発生しました。', 'danger');
            });
        });
    }
    
    // 開始時間変更時に終了時間の選択肢を更新
    var startTimeSelect = document.getElementById('startTime');
    var endTimeSelect = document.getElementById('endTime');
    
    if (startTimeSelect && endTimeSelect) {
        startTimeSelect.addEventListener('change', function() {
            var startTime = this.value;
            if (!startTime) return;
            
            // 終了時間の選択肢を更新
            var startHour = parseInt(startTime.split(':')[0]);
            endTimeSelect.innerHTML = '<option value="">選択してください</option>';
            
            for (var hour = startHour + 1; hour <= 18; hour++) {
                var timeStr = hour.toString().padStart(2, '0') + ':00';
                var option = document.createElement('option');
                option.value = timeStr;
                option.textContent = timeStr;
                endTimeSelect.appendChild(option);
            }
        });
    }
    
    // 日付入力の制限設定
    var dateInput = document.getElementById('date');
    if (dateInput) {
        // 今日の日付を設定
        var today = new Date();
        var todayStr = today.toISOString().split('T')[0];
        dateInput.setAttribute('min', todayStr);
        
        // 30日後までの制限
        var maxDate = new Date();
        maxDate.setDate(today.getDate() + 30);
        var maxDateStr = maxDate.toISOString().split('T')[0];
        dateInput.setAttribute('max', maxDateStr);
    }
});

// アラート表示関数
function showAlert(message, type) {
    // 既存のアラートを削除
    var existingAlerts = document.querySelectorAll('.custom-alert');
    existingAlerts.forEach(function(alert) {
        alert.remove();
    });
    
    // 新しいアラートを作成
    var alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-' + type + ' alert-dismissible fade show custom-alert';
    alertDiv.innerHTML = message + 
        '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
    
    document.body.appendChild(alertDiv);
    
    // 自動的に削除
    setTimeout(function() {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// 予約時間の重複チェック
function checkTimeConflict(date, startTime, endTime) {
    return fetch('/api/reservations')
        .then(response => response.json())
        .then(events => {
            for (var event of events) {
                var eventDate = event.start.split('T')[0];
                if (eventDate === date) {
                    var eventStart = event.start.split('T')[1].substring(0, 5);
                    var eventEnd = event.end.split('T')[1].substring(0, 5);
                    
                    // 時間重複チェック
                    if ((startTime >= eventStart && startTime < eventEnd) ||
                        (endTime > eventStart && endTime <= eventEnd) ||
                        (startTime <= eventStart && endTime >= eventEnd)) {
                        return true; // 重複あり
                    }
                }
            }
            return false; // 重複なし
        });
}

// カレンダー表示の色分け設定
function setEventColor(event) {
    if (event.extendedProps && event.extendedProps.isUserReservation) {
        return {
            backgroundColor: '#0d6efd',
            borderColor: '#0d6efd'
        };
    } else {
        return {
            backgroundColor: '#6c757d',
            borderColor: '#6c757d'
        };
    }
}